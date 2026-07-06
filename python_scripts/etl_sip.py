import pandas as pd
from sqlalchemy import create_engine

from mapping import SIP_MASTER_MAPPING

# =====================================================
# DATABASE CONNECTION
# =====================================================

engine = create_engine(
    "postgresql+psycopg2://postgres:postgres123@localhost:5432/tr_project"
)

# =====================================================
# CLEAN COLUMN NAMES
# =====================================================

def clean_columns(df):

    if df is None:
        return df

    df = df.copy()

    df.columns = (
        df.columns.astype(str)
        .str.lower()
        .str.strip()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
        .str.replace("/", "_", regex=False)
        .str.replace("#", "", regex=False)
    )

    return df


# =====================================================
# NORMALIZE DATA
# =====================================================

def normalize(df):

    if df is None:
        return df

    df = df.copy()

    for col in df.columns:

        if pd.api.types.is_datetime64_any_dtype(df[col]):
            continue

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


# =====================================================
# CLEAN VALUE
# =====================================================

def clean_value(v):

    if pd.isna(v):
        return ""

    return str(v).strip()


# =====================================================
# APPLY SIP MAPPING
# =====================================================

def apply_sip_mapping(raw_df, mapping):

    raw_df = clean_columns(raw_df)

    mapped_df = pd.DataFrame(index=raw_df.index)

    for target_col, source_cols in mapping.items():

        if target_col in ["flag", "created_at", "updated_at"]:
            continue

        value = None

        for src in source_cols:

            src = (
                src.lower()
                .replace(" ", "_")
                .replace("-", "_")
                .replace("/", "_")
                .replace("#", "")
            )

            if src in raw_df.columns:
                value = raw_df[src]
                break

        if value is None:
            value = pd.Series([None] * len(raw_df), index=raw_df.index)

        mapped_df[target_col] = value

    return mapped_df


# =====================================================
# DATE COLUMNS
# =====================================================

DATE_COLUMNS = [

    "registration_date",
    "start_date",
    "end_date",
    "terminate_date"

]


def format_dates(df):

    for col in DATE_COLUMNS:

        if col in df.columns:

            df[col] = pd.to_datetime(
                df[col],
                errors="coerce"
            )

    return df

# =====================================================
# PROCESS SIP MASTER
# =====================================================

def process_sip(sip_df):

    if sip_df is None or sip_df.empty:
        print("No SIP file found.")
        return

    raw_df = sip_df.copy()

    # =====================================================
    # APPLY MAPPING
    # =====================================================

    df = apply_sip_mapping(
        raw_df,
        SIP_MASTER_MAPPING
    )

    # =====================================================
    # NORMALIZE
    # =====================================================

    df = normalize(df)

    # =====================================================
    # FORMAT DATE COLUMNS
    # =====================================================

    df = format_dates(df)

    # =====================================================
    # INTEGER COLUMNS
    # =====================================================

    if "no_of_installments" in df.columns:

        df["no_of_installments"] = pd.to_numeric(
            df["no_of_installments"],
            errors="coerce"
        ).astype("Int64")

    # =====================================================
    # NUMERIC COLUMNS
    # =====================================================

    if "amount" in df.columns:

        df["amount"] = pd.to_numeric(
            df["amount"],
            errors="coerce"
        )

    # =====================================================
    # NORMALIZE UMRNCODE
    # =====================================================

    if "umrncode" in df.columns:

        df["umrncode"] = (
            df["umrncode"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
        )

    # =====================================================
    # AUDIT COLUMNS
    # =====================================================

    now = pd.Timestamp.now()

    df["created_at"] = now
    df["updated_at"] = now

    # =====================================================
    # LOAD EXISTING TABLE
    # =====================================================

    try:

        existing = pd.read_sql(
            """
            SELECT umrncode
            FROM bronze.sip_master
            """,
            engine
        )

        existing = normalize(existing)

        existing["umrncode"] = (
            existing["umrncode"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
        )

    except Exception:

        existing = pd.DataFrame(columns=["umrncode"])

        # =====================================================
    # DUPLICATE FLAG
    # =====================================================

    if existing.empty:

        df["flag"] = 0

    else:

        existing_set = set(existing["umrncode"])

        df["flag"] = (
            df["umrncode"]
            .isin(existing_set)
            .astype(int)
        )

    # =====================================================
    # RENAME TO DATABASE COLUMN NAMES
    # =====================================================

    db_mapping = {

        "zone": "Zone",
        "branch": "Branch",
        "location": "Location",
        "ihno": "Ihno",
        "folio": "Folio",
        "investor_name": "Investor Name",

        "registration_date": "RegistrationDate",
        "start_date": "Start Date",
        "end_date": "End Date",

        "no_of_installments": "No Of Installments",
        "amount": "Amount",

        "scheme": "Scheme",
        "plan": "Plan",

        "agent_code": "AgentCode",
        "agent_name": "AgentName",
        "subbroker": "Subbroker",

        "scheme_name": "Scheme Name",

        "pan": "PAN",

        "sip_type": "SipType",
        "sip_mode": "SIP Mode",

        "fund_code": "Fund Code",
        "product_code": "Product Code",

        "frequency": "Frequency",
        "trtype": "Trtype",

        "to_scheme": "To Scheme",
        "to_plan": "To Plan",

        "terminate_date": "TerminateDate",
        "status": "Status",

        "to_product_code": "ToProductCode",
        "to_scheme_name": "ToSchemeName",

        "ecsno": "ECSNO",
        "ecs_bank_name": "ECSBankName",
        "ecs_acno": "ECSAcno",
        "ecs_holder_name": "ECSHolderName",

        "reg_slno": "RegSlno",
        "inv_dp_id": "InvDpId",
        "inv_client_id": "InvClientId",
        "dp_inv_name": "DP_InvName",

        "modify_flag": "ModifyFlag",

        "umrncode": "umrncode",

        "flag": "flag",
        "created_at": "created_at",
        "updated_at": "updated_at"

    }

    df.rename(columns=db_mapping, inplace=True)

    # =====================================================
    # NULL VALUES
    # =====================================================

    df = df.where(pd.notnull(df), None)

    # =====================================================
    # DATABASE COLUMN ORDER
    # =====================================================

    db_columns = pd.read_sql(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema='bronze'
        AND table_name='sip_master'
        ORDER BY ordinal_position
        """,
        engine
    )["column_name"].tolist()

    for col in db_columns:

        if col not in df.columns:
            df[col] = None

    df = df[db_columns]

        # =====================================================
    # INSERT INTO BRONZE TABLE
    # =====================================================

    df.to_sql(

        "sip_master",
        engine,
        schema="bronze",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=5000
    )

    # =====================================================
    # LOG
    # =====================================================

    print("=" * 60)
    print("SIP ETL Completed Successfully")
    print("=" * 60)
    print(f"Inserted Rows : {len(df)}")
    print(f"Duplicate Rows : {df['flag'].sum()}")
    print("=" * 60)

    