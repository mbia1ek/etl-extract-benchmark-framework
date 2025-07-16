import duckdb
from utils.timer import Timer
import pyodbc
import pandas as pd


def run_pandas_readsql_duckdb_offload(conn_str, query, duckdb_file):
    with Timer() as t:
        conn = pyodbc.connect(conn_str)
        df = pd.read_sql_query(query, conn)
        conn.close()
        duck_conn = duckdb.connect(duckdb_file)
        duck_conn.execute("CREATE TABLE IF NOT EXISTS staging AS SELECT * FROM df")
    return t.elapsed, len(df)
