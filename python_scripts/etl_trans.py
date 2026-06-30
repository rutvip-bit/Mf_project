import pandas as pd
import numpy as np
from sqlalchemy import create_engine

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
            .replace("nan", "")
            .replace("None", "")
            .replace("<NA>", "")
        )

    return df


def clean_value(v):
    if pd.isna(v):
        return ""
    return str(v).strip()

def process_transactions(cams=None, kfin=None):

    dfs = []

    # =========================
    # CAMS MAPPING
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

            # unique CAMS
            "prodcode": get(cams, "prodcode"),
            "usercode": get(cams, "usercode"),
            "usrtrxno": get(cams, "usrtrxno"),
            "purprice": get(cams, "purprice"),
            "subbrok": get(cams, "subbrok"),

            "source": "CAMS"
        })

        cams_df = normalize(cams_df)
        dfs.append(cams_df)

    # =========================
    # KFIN MAPPING
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

            # unique KFIN
            "sno": get(kfin, "sno"),
            "td_fund": get(kfin, "td_fund"),
            "chqno": get(kfin, "chqno"),

            "source": "KFIN"
        })

        kfin_df = normalize(kfin_df)
        dfs.append(kfin_df)

        if not dfs:
             print("No transaction files found.")
             return

    df = pd.concat(dfs, ignore_index=True)
    df = df.applymap(clean_value)
    df = normalize(df)

    df["created_at"] = pd.Timestamp.now()
    df["updated_at"] = pd.Timestamp.now()

    existing = pd.read_sql(
        "SELECT * FROM bronze.transaction",
        engine
    )

    existing = normalize(existing)

    # =========================
    # FIRST LOAD CHECK
    # =========================
    if existing.empty:
        df["flag"] = 0

    else:
        ignore_cols = {"created_at", "updated_at", "flag"}

        compare_cols = [
            c for c in df.columns
            if c in existing.columns and c not in ignore_cols
        ]

        df_cmp = df[compare_cols].astype(str).fillna("")
        ex_cmp = existing[compare_cols].astype(str).fillna("")

        existing_set = set(
            ex_cmp.apply(lambda x: "|".join(x.values), axis=1)
        )

        df["flag"] = (
            df_cmp.apply(lambda x: "|".join(x.values), axis=1)
            .isin(existing_set)
            .astype(int)
        )

    # remove column if not in DB
    if "source" not in existing.columns:
        df = df.drop(columns=["source"], errors="ignore")

    df = df.where(pd.notnull(df), None)

    print("Incoming rows:", len(df))
    print("Duplicate rows:", df["flag"].sum())

    df.to_sql(
        "transaction",
        engine,
        schema="bronze",
        if_exists="append",
        index=False,
        chunksize=5000,
        method="multi"
    )

    print("Transaction ETL Completed Successfully")