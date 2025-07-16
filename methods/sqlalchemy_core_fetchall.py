from utils.timer import Timer
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


def run_sqlalchemy_core_fetchall(conn_str, query):
    url = URL.create("mssql+pyodbc", query={"odbc_connect": conn_str})
    engine = create_engine(url)
    with Timer() as t:
        with engine.connect() as connection:
            result = connection.execute(text(query))
            rows = result.fetchall()
    return t.elapsed, len(rows)
