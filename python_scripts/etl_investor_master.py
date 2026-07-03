import pandas as pd
import numpy as np

from sqlalchemy import create_engine

from mapping import INVESTOR_MASTER_MAPPING


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
# DATE COLUMNS
# =====================================================

DATE_COLUMNS = [
    "dob",
    "report_date",
    "rep_date",
    "folio_date",
    "jh1_dob",
    "jh2_dob",
    "guardian_dob",
    "lastupdateddate",
    "nominee_dob"
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
# CLEAN IDENTIFIER
# =====================================================

def clean_identifier(df, column):

    if df is None:
        return df

    if column not in df.columns:
        return df

    df = df.copy()

    df[column] = (
        df[column]
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
# APPLY INVESTOR MAPPING
# =====================================================

def apply_investor_mapping(raw_df, mapping):

    raw_df = clean_columns(raw_df)

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
# PROCESS INVESTOR MASTER
# =====================================================

def process_investor_master(cams=None, kfin=None):

    dfs = []

    # =====================================================
    # CAMS
    # =====================================================

    if cams is not None and not cams.empty:

        cams_df = apply_investor_mapping(
            cams,
            INVESTOR_MASTER_MAPPING
        )

        cams_df = normalize(cams_df)

        cams_df = clean_identifier(
            cams_df,
            "folio_no"
        )

        cams_df = format_dates(cams_df)

        dfs.append(cams_df)

    # =====================================================
    # KFIN
    # =====================================================

    if kfin is not None and not kfin.empty:

        kfin_df = apply_investor_mapping(
            kfin,
            INVESTOR_MASTER_MAPPING
        )

        kfin_df = normalize(kfin_df)

        kfin_df = clean_identifier(
            kfin_df,
            "folio_no"
        )

        kfin_df = format_dates(kfin_df)

        dfs.append(kfin_df)

    # =====================================================
    # NO FILES
    # =====================================================

    if not dfs:

        print("No Investor Master file found.")
        return

    # =====================================================
    # MERGE
    # =====================================================

    df = pd.concat(
        dfs,
        ignore_index=True
    )

    now = pd.Timestamp.now()

    df["created_at"] = now
    df["updated_at"] = now

    try:

        existing = pd.read_sql(
            "SELECT * FROM bronze.investor_master",
            engine
        )

        existing = normalize(existing)

        existing = clean_identifier(
            existing,
            "folio_no"
        )

        existing = format_dates(existing)

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

        # =====================================================
        # CLEAN IDENTIFIER BEFORE COMPARISON
        # =====================================================

        if "folio_no" in new_df.columns:

            new_df = clean_identifier(
                new_df,
                "folio_no"
            )

        if "folio_no" in old_df.columns:

            old_df = clean_identifier(
                old_df,
                "folio_no"
            )

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
    # CLEAN IDENTIFIER AGAIN BEFORE INSERT
    # =====================================================

    df = clean_identifier(
        df,
        "folio_no"
    )

    # =====================================================
    # GET COLUMN ORDER FROM POSTGRES
    # =====================================================

    db_columns = pd.read_sql(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'bronze'
        AND table_name = 'investor_master'
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
    # FINAL CLEAN IDENTIFIER
    # (ENSURES .0 NEVER REACHES POSTGRES)
    # =====================================================

    df = clean_identifier(
        df,
        "folio_no"
    )

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
    # FINAL CLEAN IDENTIFIER
    # =====================================================

    df = clean_identifier(
        df,
        "folio_no"
    )

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
    print("Loading Investor Master...")
    print(f"Rows to insert : {len(df)}")
    print("=" * 80)

    df.to_sql(
        "investor_master",
        engine,
        schema="bronze",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=5000
    )

    print("=" * 80)
    print("Investor Master Loaded Successfully")
    print(f"Inserted {len(df)} rows")
    print("=" * 80)

    return df