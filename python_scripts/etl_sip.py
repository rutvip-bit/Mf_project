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

    if df is None or df.empty:
        return df

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

    if df is None or df.empty:
        return df

    object_cols = df.select_dtypes(include=["object"]).columns

    replace_values = {
        "nan": "",
        "None": "",
        "<NA>": "",
        "NaT": ""
    }

    for col in object_cols:

        df[col] = (
            df[col]
            .fillna("")
            .astype(str)
            .str.strip()
            .replace(replace_values)
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

    normalized_columns = {}

    for col in raw_df.columns:

        normalized_columns[
            col.lower()
            .replace(" ", "_")
            .replace("-", "_")
            .replace("/", "_")
            .replace("#", "")
        ] = col

    for target_col, source_cols in mapping.items():

        if target_col in ("flag", "created_at", "updated_at"):
            continue

        mapped_df[target_col] = None

        for src in source_cols:

            src = (
                src.lower()
                .replace(" ", "_")
                .replace("-", "_")
                .replace("/", "_")
                .replace("#", "")
            )

            if src in normalized_columns:

                mapped_df[target_col] = raw_df[
                    normalized_columns[src]
                ]

                break

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
# DATABASE COLUMN ORDER
# =====================================================

DB_COLUMNS = [
    "Zone",
    "Branch",
    "Location",
    "Ihno",
    "Folio",
    "Investor Name",
    "RegistrationDate",
    "Start Date",
    "End Date",
    "No Of Installments",
    "Amount",
    "Scheme",
    "Plan",
    "AgentCode",
    "AgentName",
    "Subbroker",
    "Scheme Name",
    "PAN",
    "SipType",
    "SIP Mode",
    "Fund Code",
    "Product Code",
    "Frequency",
    "Trtype",
    "To Scheme",
    "To Plan",
    "TerminateDate",
    "Status",
    "ToProductCode",
    "ToSchemeName",
    "ECSNO",
    "ECSBankName",
    "ECSAcno",
    "ECSHolderName",
    "RegSlno",
    "InvDpId",
    "InvClientId",
    "DP_InvName",
    "ModifyFlag",
    "umrncode",
    "flag",
    "created_at",
    "updated_at"
]

# =====================================================
# PROCESS SIP MASTER
# =====================================================

def process_sip(sip_df):

    if sip_df is None or sip_df.empty:
        print("No SIP file found.")
        return

    # =====================================================
    # APPLY MAPPING
    # =====================================================

    df = apply_sip_mapping(
        sip_df,
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

        existing = pd.read_sql_query(
            """
            SELECT umrncode
            FROM bronze.sip_master
            WHERE umrncode IS NOT NULL
            """,
            engine
        )

        if not existing.empty:

            existing["umrncode"] = (
                existing["umrncode"]
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

        existing_set = frozenset(existing["umrncode"].values)

        df["flag"] = (
            df["umrncode"]
            .isin(existing_set)
            .astype("int8")
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

    for col in DB_COLUMNS:

        if col not in df.columns:
            df[col] = None

    df = df.reindex(columns=DB_COLUMNS)

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
        chunksize=20000
    )

    # =====================================================
    # LOG
    # =====================================================

    inserted_rows = len(df)
    duplicate_rows = int(df["flag"].sum())

    print("=" * 60)
    print("SIP ETL Completed Successfully")
    print("=" * 60)
    print(f"Inserted Rows : {inserted_rows}")
    print(f"Duplicate Rows : {duplicate_rows}")
    print("=" * 60)