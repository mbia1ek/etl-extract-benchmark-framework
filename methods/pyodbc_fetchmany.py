from utils.timer import Timer
import pyodbc


def run_pyodbc_fetchmany(conn_str, query, batch_size=10000):
    total_rows = 0
    with Timer() as t:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute(query)
        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch:
                break
            total_rows += len(batch)
        conn.close()
    return t.elapsed, total_rows
