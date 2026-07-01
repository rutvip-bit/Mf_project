import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

engine = create_engine(
    "postgresql+psycopg2://postgres:postgres123@localhost:5432/tr_project"
)


# =====================================================
# SAFE READ
# =====================================================
def safe_read(query):
    try:
        return pd.read_sql(query, engine)
    except Exception:
        return pd.DataFrame()


# =====================================================
# MARK BRONZE ROWS AS PROCESSED
# =====================================================
def mark_done(table_name):
    with engine.begin() as conn:
        conn.execute(text(f"""
            UPDATE bronze.{table_name}
            SET flag = 1
            WHERE flag = 0
        """))


# =====================================================
# SILVER LOAD PIPELINE
# =====================================================
def load_silver():

    transform_time = datetime.now()

    # =====================================================
    # INVESTOR MASTER
    # =====================================================
    investor_df = safe_read("""
        SELECT *
        FROM bronze.investor_master
        WHERE flag = 0
    """)

    if not investor_df.empty:

        investor_df = investor_df.drop(columns=["flag"], errors="ignore")

        investor_df["created_at"] = transform_time
        investor_df["updated_at"] = transform_time

        investor_df.to_sql(
            "investor_master",
            engine,
            schema="silver",
            if_exists="append",
            index=False,
            chunksize=5000,
            method="multi"
        )

        mark_done("investor_master")

    # =====================================================
    # TRANSACTION MASTER
    # =====================================================
    transaction_df = safe_read("""
        SELECT *
        FROM bronze.transaction_master
        WHERE flag = 0
    """)

    if not transaction_df.empty:

        transaction_df = transaction_df.drop(columns=["flag"], errors="ignore")

        transaction_df["created_at"] = transform_time
        transaction_df["updated_at"] = transform_time

        transaction_df.to_sql(
            "transaction_master",
            engine,
            schema="silver",
            if_exists="append",
            index=False,
            chunksize=5000,
            method="multi"
        )

        mark_done("transaction_master")

    # =====================================================
    # SIP MASTER
    # =====================================================
    sip_df = safe_read("""
        SELECT *
        FROM bronze.sip_master
        WHERE flag = 0
    """)

    if not sip_df.empty:

        sip_df = sip_df.drop(columns=["flag"], errors="ignore")

        sip_df["created_at"] = transform_time
        sip_df["updated_at"] = transform_time

        sip_df.to_sql(
            "sip_master",
            engine,
            schema="silver",
            if_exists="append",
            index=False,
            chunksize=5000,
            method="multi"
        )

        mark_done("sip_master")

    print("✔ Silver Layer Loaded Successfully")


# =====================================================
# RUN DIRECTLY
# =====================================================
if __name__ == "__main__":
    load_silver()