import pandas as pd
import numpy as np
from sqlalchemy import create_engine

# =========================
# POSTGRES CONNECTION
# =========================
engine = create_engine(
    "postgresql+psycopg2://postgres:postgres123@localhost:5432/tr_project"
)

# =========================
# CLEAN FUNCTIONS
# =========================
def clean_columns(df):

    if df is None:
        return df

    df = df.copy()

    df.columns = (
        df.columns.astype(str)
        .str.lower()
        .str.strip()
        .str.replace(" ", "_", regex=False)
        .str.replace("#", "", regex=False)
        .str.replace("-", "_", regex=False)
        .str.replace("/", "_", regex=False)
    )

    return df


def clean_value(v):

    if pd.isna(v):
        return ""

    if isinstance(v, pd.Timestamp):
        return str(v.date())

    return str(v).strip()


def get(df, col):

    if df is None:
        return pd.Series([])

    if col in df.columns:
        return df[col]

    return pd.Series([""] * len(df), index=df.index)


def normalize(df):

    if df is None:
        return df

    df = df.copy()

    for col in df.columns:

        df[col] = (
            df[col]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        df[col] = (
            df[col]
            .replace("nan", "")
            .replace("None", "")
            .replace("<NA>", "")
        )

    return df


# =========================
# MAIN FUNCTION
# =========================
def process_transactions(cams=None, kfin=None):

    dfs = []

    # =========================
    # CAMS
    # =========================
    if cams is not None:

        cams = clean_columns(cams)

        cams_df = pd.DataFrame({

            "source_system": "CAMS",
            "prod": get(cams, "prod"),
            "folio_no": get(cams, "folio_no"),
            "scheme": get(cams, "scheme"),
            "investor_name": get(cams, "inv_name"),
            "transaction_type": get(cams, "trxntype"),
            "transaction_no": get(cams, "trxnno"),
            "transaction_mode": get(cams, "trxnmode"),
            "transaction_status": get(cams, "trxnstat"),
            "trade_date": get(cams, "traddate"),
            "post_date": get(cams, "postdate"),
            "units": get(cams, "units"),
            "amount": get(cams, "amount"),
            "broker_code": get(cams, "brokcode"),
            "broker_percent": get(cams, "brokperc"),
            "broker_commission": get(cams, "brokcomm"),
            "location": get(cams, "ter_locati"),
            "tax_status": get(cams, "tax_status"),
            "load_amount": get(cams, "load"),
            "bank_name": get(cams, "bank_name"),
            "account_no": get(cams, "ac_no"),
            "report_date": get(cams, "rep_date"),
            "pan": get(cams, "pan"),

            # CAMS UNIQUE
            "prodcode": get(cams, "prodcode"),
            "usercode": get(cams, "usercode"),
            "usrtrxno": get(cams, "usrtrxno"),
            "purprice": get(cams, "purprice"),
            "subbrok": get(cams, "subbrok"),
            "altfolio": get(cams, "altfolio"),
            "time1": get(cams, "time1"),
            "trxnsubtyp": get(cams, "trxnsubtyp"),
            "applicatio": get(cams, "applicatio"),
            "trxn_natur": get(cams, "trxn_natur"),
            "tax": get(cams, "tax"),
            "total_tax": get(cams, "total_tax"),
            "stt": get(cams, "stt"),
            "scheme_typ": get(cams, "scheme_typ"),
            "scanrefno": get(cams, "scanrefno"),
            "exchange_flag": get(cams, "exchange_f"),
            "stamp_duty": get(cams, "stamp_duty"),

            "source": "CAMS"
        })

        cams_df = normalize(cams_df)
        dfs.append(cams_df)

    # =========================
    # KFIN
    # =========================
    if kfin is not None:

        kfin = clean_columns(kfin)

        kfin_df = pd.DataFrame({

            "source_system": "KFIN",
            "prod": get(kfin, "fmcode"),
            "folio_no": get(kfin, "td_acno"),
            "scheme": get(kfin, "funddesc"),
            "investor_name": get(kfin, "invname"),
            "transaction_type": get(kfin, "td_trtype"),
            "transaction_no": get(kfin, "td_trno"),
            "transaction_mode": get(kfin, "trnmode"),
            "transaction_status": get(kfin, "trnstat"),
            "trade_date": get(kfin, "td_trdt"),
            "post_date": get(kfin, "td_prdt"),
            "units": get(kfin, "td_units"),
            "amount": get(kfin, "td_amt"),
            "broker_code": get(kfin, "td_agent"),
            "broker_percent": get(kfin, "brokper"),
            "broker_commission": get(kfin, "brokcomm"),
            "location": get(kfin, "td_branch"),
            "tax_status": get(kfin, "status"),
            "load_amount": get(kfin, "load1"),
            "bank_name": get(kfin, "bname"),
            "account_no": get(kfin, "bnkacno"),
            "report_date": get(kfin, "crdate"),
            "pan": get(kfin, "pangno"),

            # KFIN UNIQUE (minimal)
            "sno": get(kfin, "sno"),
            "td_fund": get(kfin, "td_fund"),
            "schpln": get(kfin, "schpln"),
            "divopt": get(kfin, "divopt"),
            "chqno": get(kfin, "chqno"),
            "mobile": get(kfin, "mobile"),
            "email": get(kfin, "email"),
            "trflag": get(kfin, "trflag"),
            "source": "KFIN"
        })

        kfin_df = normalize(kfin_df)
        dfs.append(kfin_df)

    # =========================
    # NO FILES
    # =========================
    if not dfs:
        print("No transaction files found.")
        return

    # =========================
    # COMBINE DATA
    # =========================
    df = pd.concat(dfs, ignore_index=True)

    df = df.apply(lambda col: col.map(clean_value))
    df = normalize(df)

    # =========================
    # LOAD EXISTING DATA
    # =========================
    existing = pd.read_sql(
        "SELECT * FROM transaction",
        engine
    )

    existing = normalize(existing)

    # =========================
    # MATCH STRUCTURE
    # =========================
    df = df.reindex(columns=existing.columns, fill_value="")
    existing = existing.reindex(columns=df.columns, fill_value="")

    df = df.fillna("").astype(str)
    existing = existing.fillna("").astype(str)

    # strip spaces
    for col in df.columns:
        df[col] = df[col].str.strip()

    for col in existing.columns:
        existing[col] = existing[col].str.strip()

    # =========================
    # REMOVE DUPLICATES (SAME LOGIC AS INVESTOR MASTER)
    # =========================
    existing_rows = set(map(tuple, existing.values.tolist()))

    new_rows = df[~df.apply(tuple, axis=1).isin(existing_rows)]

    print(f"Incoming rows : {len(df)}")
    print(f"Existing rows : {len(existing)}")
    print(f"New rows      : {len(new_rows)}")

    # =========================
    # INSERT ONLY NEW ROWS
    # =========================
    if not new_rows.empty:

        new_rows.to_sql(
            "transaction",
            engine,
            if_exists="append",
            index=False,
            chunksize=5000,
            method="multi"
        )

        print(f"{len(new_rows)} rows inserted successfully.")

    else:
        print("No new rows found. Skipped duplicate records.")

    print("Transaction ETL Completed Successfully.")