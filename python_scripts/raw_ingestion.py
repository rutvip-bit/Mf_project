import csv
import io
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

            file.seek(0)

            text = file.read().decode("utf-8")

        except UnicodeDecodeError:

            file.seek(0)

            text = file.read().decode("latin1")

        # =====================================================
        # PARSE CSV USING SINGLE QUOTES
        # =====================================================

        reader = csv.reader(
            io.StringIO(text),
            delimiter=delimiter,
            quotechar="'",
            skipinitialspace=True
        )

        rows = list(reader)

        header = rows[0]
        expected_cols = len(header)

        clean_rows = []

        print("=" * 80)
        print("Header Columns :", expected_cols)

        bad_rows = 0

        for i, row in enumerate(rows[1:], start=2):

            if len(row) != expected_cols:

                bad_rows += 1

                print(f"\nProblem found at row {i}")
                print(f"Expected Columns : {expected_cols}")
                print(f"Found Columns    : {len(row)}")

                # Print only first few values to avoid flooding terminal
                print(row[:10])

            # Extra columns -> keep only expected columns
            if len(row) > expected_cols:
                row = row[:expected_cols]

            # Missing columns -> pad with blanks
            elif len(row) < expected_cols:
                row = row + [""] * (expected_cols - len(row))

            clean_rows.append(row)

        print("Total Bad Rows :", bad_rows)
        print("=" * 80)

        df = pd.DataFrame(
            clean_rows,
            columns=header
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
            .apply(
                lambda s: s.str.replace("'", "", regex=False)
                        .str.replace('"', "", regex=False)
                        .str.strip()
            )
            .replace({
                "nan": "",
                "None": "",
                "<NA>": ""
            })
        )

    # =====================================================
    # DEBUG
    # =====================================================

    print("\n" + "=" * 80)
    print("FILE :", file.name)
    print("ROWS READ :", len(df))
    print("TOTAL COLUMNS :", len(df.columns))
    print("COLUMN NAMES :")
    print(df.columns.tolist())

    print("\nSample Rows (1340-1355):")
    print(df.iloc[1340:1355])

    print("=" * 80 + "\n")

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