from utils.timer import Timer
import pyodbc


def run_pyodbc_fetchone(conn_str, query):
    total_rows = 0
    with Timer() as t:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute(query)
        while True:
            row = cursor.fetchone()
            if not row:
                break
            total_rows += 1
        conn.close()
    return t.elapsed, total_rows
