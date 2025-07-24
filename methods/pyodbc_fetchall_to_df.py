from utils.timer import Timer
import pyodbc
import pandas as pd


def run_pyodbc_fetchall_to_df(conn_str, query):
    with Timer() as t:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        df = pd.DataFrame.from_records(rows, columns=columns)
        conn.close()

    return t.elapsed, len(df)
