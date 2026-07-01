import pandas as pd
import numpy as np
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://postgres:postgres123@localhost:5432/tr_project"
)

# =========================
# CLEAN COLUMN NAMES
# =========================
def clean_columns(df):

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


# =========================
# SAFE COLUMN GETTER
# =========================
def get(df, col):

    if col in df.columns:
        return df[col]

    return pd.Series([""] * len(df), index=df.index)


# =========================
# NORMALIZE
# =========================
def normalize(df):

    df = df.copy()

    for col in df.columns:

        df[col] = (
            df[col]
            .fillna("")
            .astype(str)
            .str.strip()
            .replace({
                "nan": "",
                "None": "",
                "<NA>": "",
                "NaT": ""
            })
        )

    return df


# =========================
# REMOVE .0 FROM IDENTIFIERS
# =========================
def clean_identifier(df, column):

    if column not in df.columns:
        return df

    df = df.copy()

    df[column] = (
        df[column]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
    )

    return df


# =========================
# MAIN ETL
# =========================
def process_investor_master(cams=None, kfin=None):

    dfs = []

    # =========================
    # CAMS MAPPING
    # =========================
    if cams is not None:

        cams = clean_columns(cams)

        cams_df = pd.DataFrame({

            "folio_no": get(cams, "foliochk"),
            "amc_code": get(cams, "amc_code"),
            "scheme_name": get(cams, "sch_name"),

            "investor_name": get(cams, "inv_name"),
            "joint_name_1": get(cams, "jnt_name1"),
            "joint_name_2": get(cams, "jnt_name2"),

            "address1": get(cams, "address1"),
            "address2": get(cams, "address2"),
            "address3": get(cams, "address3"),

            "city": get(cams, "city"),
            "state": get(cams, "gst_state_code"),
            "country": get(cams, "country"),
            "pincode": get(cams, "pincode"),

            "dob": get(cams, "inv_dob"),

            "mobile_no": get(cams, "mobile_no"),
            "email": get(cams, "email"),
            "phone_res": get(cams, "phone_res"),
            "phone_off": get(cams, "phone_off"),

            "tax_status": get(cams, "tax_status"),
            "pan_no": get(cams, "pan_no"),

            "holding_nature": get(cams, "holding_nature"),
            "occupation": get(cams, "occupation"),

            "broker_code": get(cams, "broker_code"),

            "bank_name": get(cams, "bank_name"),
            "branch": get(cams, "branch"),
            "account_type": get(cams, "ac_type"),
            "bank_account_no": get(cams, "ac_no"),
            "ifsc_code": get(cams, "ifsc_code"),

            "demat_flag": get(cams, "demat"),

            "report_date": get(cams, "rep_date"),
            "closing_balance": get(cams, "clos_bal"),
            "rupee_balance": get(cams, "rupee_bal"),

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

            "folio_no": get(kfin, "folio"),
            "amc_code": get(kfin, "fund"),
            "scheme_name": get(kfin, "fund_description"),

            "investor_name": get(kfin, "investor_name"),
            "joint_name_1": get(kfin, "joint_name_1"),
            "joint_name_2": get(kfin, "joint_name_2"),

            "address1": get(kfin, "address_1"),
            "address2": get(kfin, "address_2"),
            "address3": get(kfin, "address_3"),

            "city": get(kfin, "city"),
            "state": get(kfin, "state"),
            "country": get(kfin, "country"),
            "pincode": get(kfin, "pincode"),

            "dob": get(kfin, "date_of_birth"),

            "mobile_no": get(kfin, "mobile_number"),
            "email": get(kfin, "email"),
            "phone_res": get(kfin, "phone_residence"),
            "phone_off": get(kfin, "phone_office"),

            "tax_status": get(kfin, "tax_status"),
            "pan_no": get(kfin, "pan_number"),

            "holding_nature": get(kfin, "mode_of_holding_description"),
            "occupation": get(kfin, "occupation_description"),

            "broker_code": get(kfin, "broker_code"),

            "bank_name": get(kfin, "bank_name"),
            "branch": get(kfin, "branch"),
            "account_type": get(kfin, "account_type"),
            "bank_account_no": get(kfin, "bankaccno"),
            "ifsc_code": get(kfin, "ifsc_code"),

            "demat_flag": get(kfin, "demat_folio_flag"),

            "report_date": get(kfin, "report_date"),
            "closing_balance": get(kfin, "closing_balance"),
            "rupee_balance": get(kfin, "rupee_balance"),

            "source": "KFIN"
        })

        kfin_df = normalize(kfin_df)

        dfs.append(kfin_df)

    # =========================
    # NO DATA
    # =========================
    if not dfs:
        print("No data found")
        return

    df = pd.concat(dfs, ignore_index=True)

    df = normalize(df)

    # =========================
    # REMOVE .0 FROM IDENTIFIERS
    # =========================
    identifier_columns = [
        "folio_no",
        "pan_no",
        "mobile_no",
        "bank_account_no",
        "broker_code",
        "ifsc_code",
        "pincode"
    ]

    for col in identifier_columns:
        df = clean_identifier(df, col)

    # =========================
    # AUDIT COLUMNS
    # =========================
    current_time = pd.Timestamp.now()

    df["created_at"] = current_time
    df["updated_at"] = current_time

    # =========================
    # EXISTING DATA
    # =========================
    existing = pd.read_sql(
        "SELECT * FROM bronze.investor_master",
        engine
    )

    existing = normalize(existing)

    # =========================
    # DUPLICATE FLAG
    # =========================
    if existing.empty:

        df["flag"] = 0

    else:

        ignore = {
            "created_at",
            "updated_at",
            "flag"
        }

        compare_cols = [
            c for c in df.columns
            if c in existing.columns and c not in ignore
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

    # =========================
    # REMOVE SOURCE IF DB DOESN'T HAVE IT
    # =========================
    if "source" not in existing.columns:
        df = df.drop(columns=["source"], errors="ignore")

    df = df.where(pd.notnull(df), None)

    print("Incoming rows :", len(df))
    print("Duplicate rows:", df["flag"].sum())

    # =========================
    # LOAD
    # =========================
    df.to_sql(
        "investor_master",
        engine,
        schema="bronze",
        if_exists="append",
        index=False,
        chunksize=5000,
        method="multi"
    )

    print("Investor Master ETL Completed Successfully")

    