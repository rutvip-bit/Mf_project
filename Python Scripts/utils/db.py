# utils/db.py

from sqlalchemy import create_engine

HOST = "localhost"
PORT = "5432"
DATABASE = "tr_project"
USER = "postgres"
PASSWORD = "postgres123"

engine = create_engine(
    f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
)