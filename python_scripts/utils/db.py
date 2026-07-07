from sqlalchemy import create_engine

import pandas as pd
 
HOST = "localhost"
PORT = "5432"
DATABASE = "tr_project"
USER = "postgres"
PASSWORD = "postgres123"
 
engine = create_engine(

    f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

)
 
 
def read_table(schema, table, limit=100):
 
    query = f"""

        SELECT *

        FROM {schema}.{table}

        ORDER BY created_at DESC

        LIMIT {limit}

    """
 
    df = pd.read_sql(query, engine)
 
    for col in ["created_at", "updated_at"]:
 
        if col in df.columns:
 
            df[col] = pd.to_datetime(df[col])
 
            # Bronze tables are timestamptz -> show in IST

            if schema == "bronze" and df[col].dt.tz is not None:

                df[col] = df[col].dt.tz_convert("Asia/Kolkata")
 
    return df
 