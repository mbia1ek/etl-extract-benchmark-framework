import pandas as pd
import pyodbc
from utils.timer import Timer


def run_pandas_readsql(conn_str, query):
    with Timer() as t:
        conn = pyodbc.connect(conn_str)
        df = pd.read_sql_query(query, conn)
        conn.close()
    return t.elapsed, len(df)
