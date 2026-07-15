import pandas as pd

from utils.db import engine
from mapping import TRANSACTION_MASTER_MAPPING


# =====================================================
# CLEAN COLUMN NAMES
# =====================================================

def clean_columns(df):

    if df is None:
        return df

    df = df.copy()

    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.strip("'")
        .str.strip('"')
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
        .str.replace("/", "_", regex=False)
        .str.replace("#", "", regex=False)
    )

    return df


# =====================================================
# DATE COLUMNS
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


# =====================================================
# IDENTIFIER COLUMNS
# (.0 SHOULD NEVER APPEAR)
# =====================================================

IDENTIFIER_COLUMNS = [

    "folio_no",
    "old_folio",
    "folio_old",
    "scheme_fol",
    "altfolio",

    "account_no",
    "bnkacno",
    "oldacno",

    "micr_no",
    "chqno",

    "request_re",
    "amc_ref_no",

    "pan",
    "pangno",

    "mobile",
    "rphone",
    "rphone1",
    "rphone2",
    "ophone",
    "ophone1",
    "ophone2",
    "bphone",

    "pin"
]


# =====================================================
# NORMALIZE
# =====================================================

def normalize(df):

    if df is None:
        return df

    df = df.copy()

    for col in df.columns:

        if col in DATE_COLUMNS:
            continue

        if pd.api.types.is_datetime64_any_dtype(df[col]):
            continue

        df[col] = (
            df[col]
            .fillna("")
            .astype(str)
            .str.replace("'", "", regex=False)
            .str.replace('"', "", regex=False)
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
# CLEAN IDENTIFIER COLUMNS
# =====================================================

def clean_identifier_columns(df):

    if df is None:
        return df

    df = df.copy()

    for col in IDENTIFIER_COLUMNS:

        if col not in df.columns:
            continue

        df[col] = (
            df[col]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.replace(r"\.0$", "", regex=True)
            .replace({
                "": None,
                "nan": None,
                "None": None,
                "<NA>": None
            })
        )

    return df


# =====================================================
# CLEAN VALUE
# =====================================================

def clean_value(value):

    if pd.isna(value):
        return None

    value = str(value).strip()

    if value.lower() in [

        "",
        "nan",
        "none",
        "<na>",
        "nat"

    ]:

        return None

    return value


# =====================================================
# FORMAT DATE COLUMNS
# =====================================================

def format_dates(df):

    if df is None:
        return df

    df = df.copy()

    for col in DATE_COLUMNS:

        if col in df.columns:

            df[col] = (
                pd.to_datetime(
                    df[col],
                    format="mixed",
                    errors="coerce"
                )
                .dt.date
            )

            df[col] = df[col].where(
                pd.notnull(df[col]),
                None
            )

    return df

# =====================================================
# APPLY TRANSACTION MAPPING
# =====================================================

def apply_transaction_mapping(raw_df, mapping, source):

    raw_df = clean_columns(raw_df)

    print("=" * 80)
    print("Rows received :", len(raw_df))
    print("Columns :", len(raw_df.columns))
    print(raw_df.columns.tolist())
    print("=" * 80)

    mapped_df = pd.DataFrame(index=raw_df.index)

    for target_col, source_cols in mapping.items():

        if target_col in [
            "flag",
            "created_at",
            "updated_at"
        ]:
            continue

        if target_col == "source_system":
            mapped_df[target_col] = source
            continue

        value = None

        for src in source_cols:

            src = (
                src.lower()
                .strip()
                .replace(" ", "_")
                .replace("-", "_")
                .replace("/", "_")
                .replace("#", "")
            )

            if src in raw_df.columns:
                value = raw_df[src]
                break

        if value is None:

            value = pd.Series(
                [None] * len(raw_df),
                index=raw_df.index
            )

        mapped_df[target_col] = value

    return mapped_df


# =====================================================
# PROCESS TRANSACTIONS
# =====================================================

def process_transactions(cams=None, kfin=None):

    dfs = []

    # =================================================
    # CAMS
    # =================================================

    if cams is not None and not cams.empty:

        cams_df = apply_transaction_mapping(
            cams,
            TRANSACTION_MASTER_MAPPING,
            "CAMS"
        )

        cams_df = normalize(cams_df)
        cams_df = clean_identifier_columns(cams_df)
        cams_df = format_dates(cams_df)

        dfs.append(cams_df)

    # =================================================
    # KFIN
    # =================================================

    if kfin is not None and not kfin.empty:

        kfin_df = apply_transaction_mapping(
            kfin,
            TRANSACTION_MASTER_MAPPING,
            "KFIN"
        )

        kfin_df = normalize(kfin_df)
        kfin_df = clean_identifier_columns(kfin_df)
        kfin_df = format_dates(kfin_df)

        dfs.append(kfin_df)

    # =================================================
    # NO FILE
    # =================================================

    if not dfs:

        print("No Transaction files found.")
        return

    # =================================================
    # MERGE
    # =================================================

    df = pd.concat(
        dfs,
        ignore_index=True
    )

    # =================================================
    # TIMESTAMPS
    # =================================================

    now = pd.Timestamp.now()

    df["created_at"] = now
    df["updated_at"] = now

    # =================================================
    # READ EXISTING BRONZE TABLE
    # =================================================

    try:

        existing = pd.read_sql(
            """
            SELECT *
            FROM bronze.transaction_master
            """,
            engine
        )

        existing = normalize(existing)
        existing = clean_identifier_columns(existing)
        existing = format_dates(existing)

    except Exception:

        existing = pd.DataFrame()

        # =====================================================
    # DUPLICATE FLAG
    # =====================================================

    ignore_cols = {
        "flag",
        "created_at",
        "updated_at",
        "source"
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

        # =====================================================
        # CLEAN IDENTIFIER COLUMNS
        # =====================================================

        new_df = clean_identifier_columns(new_df)
        old_df = clean_identifier_columns(old_df)

        # =====================================================
        # NORMALIZE FOR COMPARISON
        # =====================================================

        for col in compare_cols:

            if col in DATE_COLUMNS:

                new_df[col] = (
                    pd.to_datetime(
                        new_df[col],
                        errors="coerce"
                    )
                    .dt.strftime("%Y-%m-%d")
                    .fillna("")
                )

                old_df[col] = (
                    pd.to_datetime(
                        old_df[col],
                        errors="coerce"
                    )
                    .dt.strftime("%Y-%m-%d")
                    .fillna("")
                )

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

        # =====================================================
        # COMPLETE ROW COMPARISON
        # =====================================================

        new_keys = new_df.agg("|".join, axis=1)

        old_keys = set(
            old_df.agg("|".join, axis=1)
        )

        df["flag"] = (
            new_keys
            .isin(old_keys)
            .astype("int16")
        )

        print("=" * 80)
        print("Incoming Rows :", len(new_df))
        print("Existing Rows :", len(old_df))
        print("Duplicate Rows :", int(df["flag"].sum()))
        print("=" * 80)

    # =====================================================
    # CLEAN IDENTIFIERS AGAIN
    # =====================================================

    df = clean_identifier_columns(df)

    # =====================================================
    # GET DATABASE COLUMN ORDER
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

    # =====================================================
    # ADD MISSING COLUMNS
    # =====================================================

    for col in db_columns:

        if col not in df.columns:
            df[col] = None

    df = df[db_columns]

        # =====================================================
    # FINAL DATE CLEANING
    # =====================================================

    for col in DATE_COLUMNS:

        if col in df.columns:

            df[col] = (
                pd.to_datetime(
                    df[col],
                    errors="coerce"
                )
                .dt.date
            )

            df[col] = df[col].where(
                pd.notnull(df[col]),
                None
            )

    # =====================================================
    # CLEAN NON-DATE COLUMNS
    # =====================================================

    for col in df.columns:

        if col not in DATE_COLUMNS:

            df[col] = df[col].replace(
                {
                    "": None,
                    "nan": None,
                    "None": None,
                    "<NA>": None,
                    "NaT": None
                }
            )

    # =====================================================
    # FINAL IDENTIFIER CLEANING
    # =====================================================

    df = clean_identifier_columns(df)

    # =====================================================
    # REPLACE REMAINING NaN
    # =====================================================

    df = df.where(pd.notnull(df), None)

    # =====================================================
    # REMOVE EXACT DUPLICATES IN CURRENT FILE
    # =====================================================

    before = len(df)

    df = (
        df
        .drop_duplicates()
        .reset_index(drop=True)
    )

    print(f"Removed {before-len(df)} exact duplicate rows")

    # =====================================================
    # FINAL COLUMN ORDER
    # =====================================================

    df = df[db_columns]

    # =====================================================
    # INSERT INTO POSTGRES
    # =====================================================

    print("=" * 80)
    print("Loading Transaction Master...")
    print(f"Rows to insert : {len(df)}")
    print("=" * 80)

    df.to_sql(
        "transaction_master",
        engine,
        schema="bronze",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=5000
    )

    print("=" * 80)
    print("Transaction Master Loaded Successfully")
    print(f"Inserted {len(df)} rows")
    print(f"Duplicate Rows : {int(df['flag'].sum())}")
    print("=" * 80)

    return df