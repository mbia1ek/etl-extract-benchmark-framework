from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from utils.timer import Timer
import pandas as pd


def run_sqlalchemy_pandas_with_url(conn_str, query):
    url = URL.create("mssql+pyodbc", query={"odbc_connect": conn_str})
    engine = create_engine(url)
    with Timer() as t:
        df = pd.read_sql_query(query, engine)
    return t.elapsed, len(df)
