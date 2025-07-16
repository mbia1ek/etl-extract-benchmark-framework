import pandas as pd
from utils.timer import Timer
import pyodbc


def run_parquet_export(conn_str, query, output_file):
    with Timer() as t:
        conn = pyodbc.connect(conn_str)
        df = pd.read_sql_query(query, conn)
        conn.close()
        df.to_parquet(output_file, index=False)
    return t.elapsed, len(df)
