import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://postgres:postgres123@localhost:5432/tr_project"
)


def load_silver():

    # --------------------------
    # Investor Master
    # --------------------------
    investor_df = pd.read_sql(
        """
        SELECT *
        FROM bronze.investor_master
        WHERE flag = 0
        """,
        engine
    )

    investor_df = investor_df.drop(columns=["flag"], errors="ignore")

    investor_df.to_sql(
        "investor_master",
        engine,
        schema="silver",
        if_exists="replace",
        index=False,
        chunksize=5000,
        method="multi"
    )

    # --------------------------
    # Transaction
    # --------------------------
    transaction_df = pd.read_sql(
        """
        SELECT *
        FROM bronze.transaction
        WHERE flag = 0
        """,
        engine
    )

    transaction_df = transaction_df.drop(columns=["flag"], errors="ignore")

    transaction_df.to_sql(
        "transaction",
        engine,
        schema="silver",
        if_exists="replace",
        index=False,
        chunksize=5000,
        method="multi"
    )

    # --------------------------
    # SIP (NEW ADDITION)
    # --------------------------
    sip_df = pd.read_sql(
        """
        SELECT *
        FROM bronze.sip_info
        WHERE flag = 0
        """,
        engine
    )

    sip_df = sip_df.drop(columns=["flag"], errors="ignore")

    sip_df.to_sql(
        "sip_info",
        engine,
        schema="silver",
        if_exists="replace",
        index=False,
        chunksize=5000,
        method="multi"
    )

    print("Silver Layer Loaded Successfully.")