import pyodbc


def get_connection(conn_str):
    return pyodbc.connect(conn_str)
