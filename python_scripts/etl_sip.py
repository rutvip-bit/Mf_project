import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://postgres:postgres123@localhost:5432/tr_project"
)


def process_sip(file):

    # =========================
    # LOAD FILE
    # =========================
    df = pd.read_excel(file)
    df["flag"] = 0

    # =========================
    # LOAD EXISTING DATA
    # =========================
    try:
        existing = pd.read_sql(
            "SELECT * FROM bronze.sip_info",
            engine
        )
    except:
        existing = pd.DataFrame(columns=df.columns)

    # =========================
    # NORMALIZE (same as transaction ETL style)
    # =========================
    df = df.fillna("").astype(str)
    existing = existing.fillna("").astype(str)

    # =========================
    # MATCH STRUCTURE (IMPORTANT SAME AS TRANSACTION)
    # =========================
    df = df.reindex(columns=existing.columns, fill_value="")
    existing = existing.reindex(columns=df.columns, fill_value="")

    # =========================
    # STRIP SPACES (same pattern)
    # =========================
    for col in df.columns:
        df[col] = df[col].str.strip()
        existing[col] = existing[col].str.strip()

    # =========================
    # FAST DUPLICATE CHECK (OPTIMIZED VERSION)
    # =========================
    compare_cols = [col for col in df.columns if col != "flag"]

    # create fast comparable key (vectorized, same logic idea as transaction but faster)
    df["_key"] = df[compare_cols].agg("||".join, axis=1)
    existing["_key"] = existing[compare_cols].agg("||".join, axis=1)

    existing_keys = set(existing["_key"])

    df["flag"] = df["_key"].isin(existing_keys).astype(int)

    # cleanup
    df.drop(columns=["_key"], inplace=True)
    existing.drop(columns=["_key"], inplace=True)

    # =========================
    # LOGS (same as transaction ETL style)
    # =========================
    print(f"Incoming rows  : {len(df)}")
    print(f"Existing rows  : {len(existing)}")
    print(f"Duplicate rows : {df['flag'].sum()}")
    print(f"Unique rows    : {(df['flag'] == 0).sum()}")

    # =========================
    # INSERT ALL ROWS (same as transaction ETL)
    # =========================
    df.to_sql(
        "sip_info",
        engine,
        schema="bronze",
        if_exists="append",
        index=False,
        chunksize=5000,
        method="multi"
    )

    print("SIP ETL Completed Successfully.")