import pyodbc
import polars as pl
from utils.timer import Timer


def run_pyodbc_fetchall_polars_offload(conn_str, query):
    with Timer() as t:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        rows = [tuple(row) for row in cursor.fetchall()]
        conn.close()
        df = pl.DataFrame(rows, schema=columns)
    return t.elapsed, df.height
