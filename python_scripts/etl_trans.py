import pandas as pd
from sqlalchemy import create_engine
 
from mapping import TRANSACTION_MASTER_MAPPING
 
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
# APPLY TRANSACTION MAPPING
# =====================================================
 
def apply_transaction_mapping(raw_df, mapping, source_name):
 
    raw_df = clean_columns(raw_df)
 
    mapped_df = pd.DataFrame(index=raw_df.index)
 
    for target_col, source_cols in mapping.items():
 
        # Static source
        if target_col == "source_system":
            mapped_df[target_col] = source_name
            continue
 
        # Skip audit columns
        if target_col in ["flag", "created_at", "updated_at"]:
            continue
 
        value = None
 
        for src in source_cols:
 
            src = src.lower()
 
            if src in raw_df.columns:
                value = raw_df[src]
                break
 
        if value is None:
            value = pd.Series([None] * len(raw_df), index=raw_df.index)
 
        mapped_df[target_col] = value
 
    return mapped_df
 
 
# =====================================================
# FORMAT DATE COLUMNS
# =====================================================
 
DATE_COLUMNS = [
 
    "trade_date",
    "post_date",
    "report_date",
    "sys_regn_d",
    "dob",
    "purdate",
    "sfunddt",
    "chqdate"
 
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
# PROCESS TRANSACTION MASTER
# =====================================================
 
def process_transactions(cams=None, kfin=None):
 
    dfs = []
 
    # =====================================================
    # CAMS
    # =====================================================
 
    if cams is not None and not cams.empty:
 
        cams_df = apply_transaction_mapping(
            cams,
            TRANSACTION_MASTER_MAPPING,
            "CAMS"
        )
 
        cams_df = normalize(cams_df)     
        cams_df = format_dates(cams_df)
 
        dfs.append(cams_df)
 
    # =====================================================
    # KFIN
    # =====================================================
 
    if kfin is not None and not kfin.empty:
 
        kfin_df = apply_transaction_mapping(
            kfin,
            TRANSACTION_MASTER_MAPPING,
            "KFIN"
        )
 
        kfin_df = format_dates(kfin_df)
        kfin_df = normalize(kfin_df)
 
        dfs.append(kfin_df)
 
    # =====================================================
    # NO FILE
    # =====================================================
 
    if not dfs:
        print("No Transaction file found.")
        return
 
    # =====================================================
    # MERGE
    # =====================================================
 
    df = pd.concat(dfs, ignore_index=True)
 
    df = normalize(df)
    df = format_dates(df)
 
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
            "SELECT * FROM bronze.transaction_master",
            engine
        )
 
        existing = normalize(existing)
 
    except Exception:
 
        existing = pd.DataFrame()
 
    # =====================================================
    # DUPLICATE FLAG
    # =====================================================
 
    ignore_cols = {
        "flag",
        "created_at",
        "updated_at"
    }
 
    if existing.empty:
 
        df["flag"] = 0
 
    else:
 
        compare_cols = [
 
            c
 
            for c in df.columns
 
            if c in existing.columns
 
            and c not in ignore_cols
 
        ]
 
        new_df = df[compare_cols].copy()
        old_df = existing[compare_cols].copy()
 
        # Make both dataframes identical
        for col in compare_cols:
 
            if col in DATE_COLUMNS:
 
                new_df[col] = pd.to_datetime(
                    new_df[col],
                    errors="coerce"
                ).dt.strftime("%Y-%m-%d")
 
                old_df[col] = pd.to_datetime(
                    old_df[col],
                    errors="coerce"
                ).dt.strftime("%Y-%m-%d")
 
            else:
 
                new_df[col] = (
                    new_df[col]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                )
 
                old_df[col] = (
                    old_df[col]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                )
 
        new_key = new_df.fillna("").agg("|".join, axis=1)
 
        old_key = set(
            old_df.fillna("").agg("|".join, axis=1)
        )
 
        df["flag"] = new_key.isin(old_key).astype(int)
 
    # =====================================================
    # NULL VALUES
    # =====================================================
 
    df = df.where(pd.notnull(df), None)
 
    # =====================================================
    # COLUMN ORDER
    # =====================================================
 
    db_columns = pd.read_sql(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema='bronze'
        AND table_name='transaction_master'
        ORDER BY ordinal_position
        """,
        engine
    )["column_name"].tolist()
 
    for col in db_columns:
 
        if col not in df.columns:
            df[col] = None
 
    df = df[db_columns]
 
    # =====================================================
    # INSERT
    # =====================================================
 
    df.to_sql(
 
        "transaction_master",
 
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
    print("Transaction ETL Completed Successfully")
    print("=" * 60)
    print(f"Inserted Rows : {len(df)}")
    print(f"Duplicate Rows : {df['flag'].sum()}")
    print("=" * 60)