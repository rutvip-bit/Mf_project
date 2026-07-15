import pandas as pd

from utils.db import engine
from mapping import SIP_MASTER_MAPPING


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

    "from_date",
    "to_date",
    "cease_date",
    "reg_date",
    "pause_from_date",
    "pause_to_date"

]


# =====================================================
# IDENTIFIER COLUMNS
# (.0 SHOULD NEVER APPEAR)
# =====================================================

IDENTIFIER_COLUMNS = [

    "folio_no",
    "folio_old",
    "scheme_folio_number",

    "instrm_no",
    "cheq_micr_no",

    "request_ref_no",
    "ft_sip_regno",

    "pan"

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
                    errors="coerce",
                    dayfirst=False
                )
                .dt.date
            )

            df[col] = df[col].where(
                pd.notnull(df[col]),
                None
            )

    return df

# =====================================================
# APPLY SIP MAPPING
# =====================================================

def apply_sip_mapping(raw_df, mapping):

    raw_df = clean_columns(raw_df)

    print("=" * 80)
    print("Rows received for mapping :", len(raw_df))
    print("Columns :", len(raw_df.columns))
    print(raw_df.columns.tolist())
    print(raw_df.head())
    print("=" * 80)

    mapped_df = pd.DataFrame(index=raw_df.index)

    for target_col, source_cols in mapping.items():

        if target_col in [
            "flag",
            "created_at",
            "updated_at"
        ]:
            continue

        value = None

        for src in source_cols:

            src = src.lower()

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
# PROCESS SIP
# =====================================================

def process_sip(sip_df, source):

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

    df = normalize(df)

    # CLEAN ALL IDENTIFIER COLUMNS
    df = clean_identifier_columns(df)

    df = format_dates(df)

    # =====================================================
    # SOURCE
    # =====================================================

    df["source"] = source

    now = pd.Timestamp.now()

    df["created_at"] = now
    df["updated_at"] = now

    try:

        existing = pd.read_sql(
            "SELECT * FROM bronze.sip_master_new",
            engine
        )

        existing = normalize(existing)

        # CLEAN ALL IDENTIFIER COLUMNS
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
        # CLEAN IDENTIFIER COLUMNS BEFORE COMPARISON
        # =====================================================

        new_df = clean_identifier_columns(new_df)

        old_df = clean_identifier_columns(old_df)

        # =====================================================
        # NORMALIZE VALUES
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
        # COMPARE COMPLETE ROW
        # =====================================================

        new_keys = new_df.agg("|".join, axis=1)

        old_keys = set(
            old_df.agg("|".join, axis=1)
        )

        df["flag"] = new_keys.isin(old_keys).astype(int)

    # =====================================================
    # CLEAN IDENTIFIER COLUMNS AGAIN BEFORE INSERT
    # =====================================================

    df = clean_identifier_columns(df)

    # =====================================================
    # GET COLUMN ORDER FROM POSTGRES
    # =====================================================

    db_columns = pd.read_sql(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'bronze'
        AND table_name = 'sip_master_new'
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

    # =====================================================
    # KEEP ONLY DATABASE COLUMNS
    # =====================================================

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

            df[col] = (
                df[col]
                .replace({
                    "": None,
                    "nan": None,
                    "None": None,
                    "<NA>": None,
                    "NaT": None
                })
            )

    # =====================================================
    # FINAL CLEAN IDENTIFIER COLUMNS
    # (ENSURES .0 NEVER REACHES POSTGRES)
    # =====================================================

    df = clean_identifier_columns(df)

    # =====================================================
    # DEBUG DATE COLUMNS
    # =====================================================

    print("=" * 80)
    print("Checking DATE columns before insert")

    for col in DATE_COLUMNS:

        if col in df.columns:

            print(f"{col} : {df[col].dtype}")

            bad = df[df[col].astype(str) == ""]

            if len(bad):

                print(f"{col} has {len(bad)} empty strings")

            print(df[col].head())

    print("=" * 80)

    # =====================================================
    # REPLACE REMAINING NaN
    # =====================================================

    df = df.where(pd.notnull(df), None)

    # =====================================================
    # FINAL SAFETY CHECK FOR DATE COLUMNS
    # =====================================================

    for col in DATE_COLUMNS:

        if col in df.columns:

            df.loc[
                df[col].astype(str).isin(
                    ["", "NaT", "nan", "None"]
                ),
                col
            ] = None

    # =====================================================
    # FINAL CLEAN IDENTIFIER COLUMNS
    # =====================================================

    df = clean_identifier_columns(df)

    # =====================================================
    # REMOVE EXACT DUPLICATE ROWS
    # =====================================================

    before = len(df)

    df = (
        df
        .drop_duplicates(keep="first")
        .reset_index(drop=True)
    )

    print(f"Removed {before - len(df)} exact duplicate rows")

    # =====================================================
    # FINAL COLUMN ORDER CHECK
    # =====================================================

    df = df[db_columns]

    # =====================================================
    # INSERT INTO POSTGRES
    # =====================================================

    print("=" * 80)
    print("Loading SIP Master...")
    print(f"Rows to insert : {len(df)}")
    print("=" * 80)

    df.to_sql(
        "sip_master_new",
        engine,
        schema="bronze",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=5000
    )

    print("=" * 80)
    print("SIP Master Loaded Successfully")
    print(f"Inserted {len(df)} rows")
    print("=" * 80)

    return df