import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://postgres:postgres123@localhost:5432/tr_project"
)

# =====================================================
# CLEAN COLUMN NAMES
# =====================================================
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


# =====================================================
# GET SAFE COLUMN
# =====================================================
def get(df, col):

    if col in df.columns:
        return df[col]

    return pd.Series([""] * len(df), index=df.index)


# =====================================================
# NORMALIZE
# =====================================================
def normalize(df):

    df = df.copy()

    for col in df.columns:

        df[col] = (
            df[col]
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


# =====================================================
# SIP ETL
# =====================================================
def process_sip(file):

    raw_df = pd.read_excel(file)
    raw_df = clean_columns(raw_df)

    # =====================================================
    # MAP TO FINAL DB SCHEMA (EXACT COLUMN NAMES)
    # =====================================================
    df = pd.DataFrame({

        "Zone": get(raw_df, "zone"),
        "Branch": get(raw_df, "branch"),
        "Location": get(raw_df, "location"),
        "Ihno": get(raw_df, "ihno"),
        "Folio": get(raw_df, "folio"),
        "Investor Name": get(raw_df, "investor_name"),

        "RegistrationDate": get(raw_df, "registrationdate"),
        "Start Date": get(raw_df, "start_date"),
        "End Date": get(raw_df, "end_date"),

        "No Of Installments": get(raw_df, "no_of_installments"),
        "Amount": get(raw_df, "amount"),

        "Scheme": get(raw_df, "scheme"),
        "Plan": get(raw_df, "plan"),

        "AgentCode": get(raw_df, "agentcode"),
        "AgentName": get(raw_df, "agentname"),
        "Subbroker": get(raw_df, "subbroker"),

        "Scheme Name": get(raw_df, "scheme_name"),
        "PAN": get(raw_df, "pan"),

        "SipType": get(raw_df, "siptype"),
        "SIP Mode": get(raw_df, "sip_mode"),

        "Fund Code": get(raw_df, "fund_code"),
        "Product Code": get(raw_df, "product_code"),
        "Frequency": get(raw_df, "frequency"),
        "Trtype": get(raw_df, "trtype"),

        "To Scheme": get(raw_df, "to_scheme"),
        "To Plan": get(raw_df, "to_plan"),

        "TerminateDate": get(raw_df, "terminatedate"),
        "Status": get(raw_df, "status"),

        "ToProductCode": get(raw_df, "toproductcode"),
        "ToSchemeName": get(raw_df, "toschemename"),

        "ECSNO": get(raw_df, "ecsno"),
        "ECSBankName": get(raw_df, "ecsbankname"),
        "ECSAcno": get(raw_df, "ecsacno"),
        "ECSHolderName": get(raw_df, "ecsholdername"),

        "RegSlno": get(raw_df, "regslno"),
        "InvDpId": get(raw_df, "invdpid"),
        "InvClientId": get(raw_df, "invclientid"),
        "DP_InvName": get(raw_df, "dp_invname"),

        "ModifyFlag": get(raw_df, "modifyflag"),
        "umrncode": get(raw_df, "umrncode"),
    })

    # =====================================================
    # NORMALIZE (ONLY FOR LOGIC, NOT FOR DB COLUMNS)
    # =====================================================
    df_norm = df.copy()

    for col in ["umrncode"]:
        df_norm[col] = (
            df_norm[col].astype(str).str.strip().str.lower()
        )

    # =====================================================
    # AUDIT COLUMNS
    # =====================================================
    ##current_time = pd.Timestamp.now()##
    ##df["created_at"] = current_time##
    ##df["updated_at"] = current_time##
    df["flag"] = 0

    # =====================================================
    # DUPLICATE LOGIC
    # =====================================================
    try:
        existing = pd.read_sql('SELECT "umrncode" FROM bronze.sip_info', engine)
    except:
        existing = pd.DataFrame(columns=["umrncode"])

    if not existing.empty:
        existing["umrncode"] = (
            existing["umrncode"].astype(str).str.strip().str.lower()
        )

        existing_set = set(existing["umrncode"])

        df["flag"] = df_norm["umrncode"].isin(existing_set).astype(int)

    # =====================================================
    # LOAD
    # =====================================================
    df = df.where(pd.notnull(df), None)

    df.to_sql(
        "sip_info",
        engine,
        schema="bronze",
        if_exists="append",
        index=False,
        chunksize=1000,
        method="multi"
    )

    print("SIP ETL Completed")