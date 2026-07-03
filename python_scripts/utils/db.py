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
 
    try:
        query = f"""
            SELECT *
            FROM {schema}.{table}
            ORDER BY created_at DESC
            LIMIT {limit}
        """
 
        return pd.read_sql(query, engine)
 
    except Exception as e:
        print("READ ERROR:", e)
        raise