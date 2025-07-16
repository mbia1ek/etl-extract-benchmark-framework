from utils.timer import Timer
import pyodbc


def run_pyodbc_fetchall(conn_str, query):
    with Timer() as t:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
    return t.elapsed, len(rows)
