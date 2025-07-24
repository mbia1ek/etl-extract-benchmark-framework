from utils.timer import Timer
import pyodbc
import pandas as pd


def run_pyodbc_fetchone_to_df(conn_str, query):
    total_rows = 0
    all_rows = []
    with Timer() as t:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        while True:
            row = cursor.fetchone()
            if not row:
                break
            all_rows.append(row)
            total_rows += 1
        conn.close()
    df = pd.DataFrame.from_records(all_rows, columns=columns)
    return t.elapsed, len(df)
