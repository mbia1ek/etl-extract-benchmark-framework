import yaml
import pandas as pd
from utils.resource_monitor import ResourceMonitor
from methods import (
    pandas_readsql,
    pandas_readsql_duckdb_offload,
    pyodbc_fetchall_polars_offload,
    pyodbc_fetchall,
    pyodbc_fetchmany,
    pyodbc_fetchone,
    bcp_export,
    csv_exporter,
    parquet_exporter,
    sqlalchemy_core_fetchall,
    sqlalchemy_pandas_read,
)

method_map = {
    'pandas_readsql': pandas_readsql.run_pandas_readsql,
    'pyodbc_fetchall': pyodbc_fetchall.run_pyodbc_fetchall,
    'pyodbc_fetchmany': lambda conn, q: pyodbc_fetchmany.run_pyodbc_fetchmany(conn, q, batch_size=1000),
    'pyodbc_fetchone': pyodbc_fetchone.run_pyodbc_fetchone,
    'bcp_export': lambda conn, q: bcp_export.run_bcp_export(conn, q, "results/bcp_output.bcp"),
    'pandas_readsql_duckdb_offload': lambda conn, q: pandas_readsql_duckdb_offload.run_pandas_readsql_duckdb_offload(
        conn, q, "results/duckdb_output.duckdb"
    ),
    'pyodbc_fetchall_polars_offload': lambda conn, q: pyodbc_fetchall_polars_offload.run_pyodbc_fetchall_polars_offload(conn, q),
    'csv_exporter': lambda conn, q: csv_exporter.run_csv_export(conn, q, "results/csv_output.csv"),
    'parquet_exporter': lambda conn, q: parquet_exporter.run_parquet_export(conn, q, "results/parquet_output.parquet"),
    'sqlalchemy_core_fetchall': lambda conn, q: sqlalchemy_core_fetchall.run_sqlalchemy_core_fetchall(conn, q),
    'sqlalchemy_pandas_read': lambda conn, q: sqlalchemy_pandas_read.run_sqlalchemy_pandas_with_url(conn, q),
}

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

results = []
for method_name in config['methods']:
    print(f"Running method: {method_name}")
    method_func = method_map.get(method_name)
    if method_func:
        monitor = ResourceMonitor(interval=config['monitoring']['interval'])
        monitor.start()
        elapsed, row_count = method_func(config['database']['conn_str'], config['database']['query'])
        monitor.stop()

        monitor_df = monitor.get_data()
        monitor_df.to_csv(f"results/{method_name}_monitor.csv", index=False)

        results.append(
            {
                'method': method_name,
                'elapsed_sec': elapsed,
                'row_count': row_count,
                'avg_cpu_percent': monitor_df['cpu_percent'].mean(),
                'avg_mem_mb': monitor_df['mem_mb'].mean(),
            }
        )


summary_df = pd.DataFrame(results)
summary_df.to_csv("results/summary.csv", index=False)
print(summary_df)
