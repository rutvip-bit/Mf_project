import csv
import pandas as pd

from etl_investor_master import process_investor_master
from etl_trans import process_transactions
from etl_sip import process_sip


# =====================================================
# READ FILE
# =====================================================

def read_file(file):

    name = file.name.lower()

    # =================================================
    # CSV / TXT
    # =================================================
    if name.endswith((".csv", ".txt")):

        file.seek(0)

        # Read a small sample to detect delimiter
        sample = file.read(4096).decode("utf-8", errors="ignore")
        file.seek(0)

        try:
            delimiter = csv.Sniffer().sniff(
                sample,
                delimiters=[",", "\t", ";", "|"]
            ).delimiter
        except Exception:
            delimiter = ","

        try:
            df = pd.read_csv(
                file,
                sep=delimiter,
                dtype=str,
                keep_default_na=False,
                low_memory=False
            )

        except UnicodeDecodeError:

            file.seek(0)
            sample = file.read(500).decode("utf-8", errors="ignore")
            print(sample[:500])
            file.seek(0)

            df = pd.read_csv(
                file,
                sep=delimiter,
                encoding="latin1",
                dtype=str,
                keep_default_na=False,
                low_memory=False
            )

    # =================================================
    # EXCEL
    # =================================================
    else:

        file.seek(0)

        df = pd.read_excel(
            file,
            dtype=str,
            keep_default_na=False
        )

    # =====================================================
    # CLEAN COLUMN NAMES
    # =====================================================

    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.strip("'")
        .str.strip('"')
    )

    # =====================================================
    # CLEAN VALUES
    # =====================================================

    object_cols = df.select_dtypes(include="object").columns

    if len(object_cols):

        df[object_cols] = (
            df[object_cols]
            .astype(str)
            .replace(
                {
                    r"^'": "",
                    r"'$": "",
                    "nan": "",
                    "None": "",
                    "<NA>": ""
                },
                regex=True
            )
            .apply(lambda s: s.str.strip())
        )

    return df


# =====================================================
# EXTRACT
# =====================================================

def extract_and_push(uploaded_files):

    transaction_files = []
    investor_files = []
    sip_files = []

    for file in uploaded_files:

        name = file.name.lower()

        df = read_file(file)

        if "trans" in name:

            transaction_files.append(df)

        elif "inv" in name:

            investor_files.append(df)

        elif "sip" in name:

            sip_files.append(df)

    # =================================================
    # PROCESS TRANSACTION
    # =================================================

    if transaction_files:

        process_transactions(transaction_files)

    # =================================================
    # PROCESS INVESTOR
    # =================================================

    if investor_files:

        investor_df = pd.concat(
            investor_files,
            ignore_index=True
        )

        process_investor_master(cams=investor_df)

    # =================================================
    # PROCESS SIP
    # =================================================

    if sip_files:

        for df in sip_files:

            process_sip(df)

    return (
        len(transaction_files),
        len(investor_files),
        len(sip_files),
    )