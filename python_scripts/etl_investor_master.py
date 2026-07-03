import pandas as pd
from sqlalchemy import create_engine

from mapping import INVESTOR_MASTER_MAPPING

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
# SAFE GET
# =====================================================
def get(df, cols):

    if isinstance(cols, str):
        cols = [cols]

    for col in cols:

        col = (
            col.lower()
            .replace(" ", "_")
            .replace("#", "")
            .replace("-", "_")
            .replace("/", "_")
        )

        if col in df.columns:
            return df[col]

    return pd.Series([None] * len(df), index=df.index)


# =====================================================
# APPLY MAPPING
# =====================================================
def apply_mapping(df):

    mapped = {}

    for target, source_cols in INVESTOR_MASTER_MAPPING.items():

        mapped[target] = get(df, source_cols)

    return pd.DataFrame(mapped)


# =====================================================
# NORMALIZE
# =====================================================
def normalize(df):

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
# REMOVE .0
# =====================================================
def clean_identifier(df, column):

    if column not in df.columns:
        return df

    df[column] = (
        df[column]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
    )

    return df


# =====================================================
# PROCESS
# =====================================================
def process_investor_master(cams=None, kfin=None):

    mapped_frames = []

    # -------------------------------------------------
    # CAMS
    # -------------------------------------------------
    if cams is not None and not cams.empty:

        cams = clean_columns(cams)
        cams = apply_mapping(cams)

        mapped_frames.append(cams)

    # -------------------------------------------------
    # KFIN
    # -------------------------------------------------
    if kfin is not None and not kfin.empty:

        kfin = clean_columns(kfin)
        kfin = apply_mapping(kfin)

        mapped_frames.append(kfin)

    # -------------------------------------------------
    # NO DATA
    # -------------------------------------------------
    if not mapped_frames:

        print("No Investor Master data found.")
        return

    # -------------------------------------------------
    # MERGE
    # -------------------------------------------------
    df = pd.concat(mapped_frames, ignore_index=True)

    # -------------------------------------------------
    # NORMALIZE
    # -------------------------------------------------
    df = normalize(df)

    # -------------------------------------------------
    # REMOVE .0 FROM IDENTIFIERS
    # -------------------------------------------------
    identifier_cols = [
        "folio_no",
        "pan_no",
        "joint1_pan",
        "joint2_pan",
        "guardian_pan",
        "mobile_no",
        "bank_account_no",
        "broker_code",
        "ifsc_code",
        "pincode",
        "dp_id",
        "ckyc_no",
        "jh1_ckyc",
        "jh2_ckyc",
        "guardian_ckyc_no"
    ]

    for col in identifier_cols:

        df = clean_identifier(df, col)

    # -------------------------------------------------
    # DATE COLUMNS
    # -------------------------------------------------
    date_cols = [
        "dob",
        "report_date",
        "folio_date"
    ]

    for col in date_cols:

        if col in df.columns:

            df[col] = pd.to_datetime(
                df[col],
                errors="coerce"
            )

    # -------------------------------------------------
    # EXISTING DATA
    # -------------------------------------------------
    try:

        existing = pd.read_sql(
            "SELECT * FROM bronze.investor_master",
            engine
        )

        existing = normalize(existing)

        for col in identifier_cols:

            existing = clean_identifier(existing, col)

    except:

        existing = pd.DataFrame()

    # -------------------------------------------------
    # DUPLICATE FLAG
    # -------------------------------------------------
    ignore = {
        "created_at",
        "updated_at",
        "flag"
    }

    if existing.empty:

        df["flag"] = 0

    else:

        compare_cols = [
            c
            for c in df.columns
            if c in existing.columns and c not in ignore
        ]

        df_cmp = df[compare_cols].copy()
        ex_cmp = existing[compare_cols].copy()

        # Normalize both dataframes identically
        df_cmp = (
            df_cmp.fillna("")
            .astype(str)
            .apply(lambda col: col.str.strip())
        )

        ex_cmp = (
            ex_cmp.fillna("")
            .astype(str)
            .apply(lambda col: col.str.strip())
        )

        df_keys = df_cmp.agg("|".join, axis=1)
        ex_keys = set(ex_cmp.agg("|".join, axis=1))

        df["flag"] = df_keys.isin(ex_keys).astype(int)

    # -------------------------------------------------
    # AUDIT
    # -------------------------------------------------
    now = pd.Timestamp.now()

    df["created_at"] = now
    df["updated_at"] = now

    # -------------------------------------------------
    # REMOVE EXTRA COLUMNS
    # -------------------------------------------------
    if not existing.empty:

        extra = set(df.columns) - set(existing.columns)

        if extra:

            df = df.drop(columns=list(extra))

    # -------------------------------------------------
    # NULLS
    # -------------------------------------------------
    df = df.where(pd.notnull(df), None)

    print(f"Incoming Rows : {len(df)}")
    print(f"Duplicate Rows: {df['flag'].sum()}")

    # -------------------------------------------------
    # LOAD
    # -------------------------------------------------
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