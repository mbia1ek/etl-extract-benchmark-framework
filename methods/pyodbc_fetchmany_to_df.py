from utils.timer import Timer
import pyodbc
import pandas as pd


def run_pyodbc_fetchmany_to_df(conn_str, query, batch_size=10000):
    total_rows = 0
    all_rows = []
    with Timer() as t:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch:
                break
            all_rows.extend(batch)
            total_rows += len(batch)
        conn.close()
    df = pd.DataFrame.from_records(all_rows, columns=columns)
    return t.elapsed, len(df)
