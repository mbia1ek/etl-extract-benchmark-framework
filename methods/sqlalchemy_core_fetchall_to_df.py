from utils.timer import Timer
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
import pandas as pd


def run_sqlalchemy_core_fetchall_to_df(conn_str, query):
    url = URL.create("mssql+pyodbc", query={"odbc_connect": conn_str})
    engine = create_engine(url)
    with Timer() as t:
        with engine.connect() as connection:
            result = connection.execute(text(query))
            rows = result.fetchall()
            columns = result.keys()
            df = pd.DataFrame(rows, columns=columns)
    return t.elapsed, len(df)
