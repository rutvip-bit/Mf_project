import pandas as pd
from sqlalchemy import create_engine, text

engine = create_engine(
    "postgresql+psycopg2://postgres:postgres123@localhost:5432/tr_project"
)


def safe_read(query):
    try:
        return pd.read_sql(query, engine)
    except Exception:
        return pd.DataFrame()


def load_silver():

    # =========================
    # INVESTOR MASTER
    # =========================
    investor_df = safe_read("""
        SELECT *
        FROM bronze.investor_master
        WHERE flag = 0
    """)

    if not investor_df.empty:

        investor_df = investor_df.drop(columns=["flag"], errors="ignore")

        with engine.begin() as conn:
            conn.execute(text("TRUNCATE TABLE silver.investor_master"))

        investor_df.to_sql(
            "investor_master",
            engine,
            schema="silver",
            if_exists="append",
            index=False,
            chunksize=5000,
            method="multi"
        )

    # =========================
    # TRANSACTION
    # =========================
    transaction_df = safe_read("""
        SELECT *
        FROM bronze."transaction"
        WHERE flag = 0
    """)

    if not transaction_df.empty:

        transaction_df = transaction_df.drop(columns=["flag"], errors="ignore")

        with engine.begin() as conn:
            conn.execute(text('TRUNCATE TABLE silver."transaction"'))

        transaction_df.to_sql(
            "transaction",
            engine,
            schema="silver",
            if_exists="append",
            index=False,
            chunksize=5000,
            method="multi"
        )

    # =========================
    # SIP INFO
    # =========================
    sip_df = safe_read("""
        SELECT *
        FROM bronze.sip_info
        WHERE flag = 0
    """)

    if not sip_df.empty:

        sip_df = sip_df.drop(columns=["flag"], errors="ignore")

        with engine.begin() as conn:
            conn.execute(text("TRUNCATE TABLE silver.sip_info"))

        sip_df.to_sql(
            "sip_info",
            engine,
            schema="silver",
            if_exists="append",
            index=False,
            chunksize=5000,
            method="multi"
        )

    print("Silver Layer Loaded Successfully")