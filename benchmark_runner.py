import yaml
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from utils.resource_monitor import ResourceMonitor
from methods import (
    pyodbc_pandas_read_sql_query,
    pandas_readsql_duckdb_offload,
    pyodbc_fetchall_polars_offload,
    pyodbc_fetchall,
    pyodbc_fetchmany,
    pyodbc_fetchone,
    bcp_export,
    csv_exporter,
    parquet_exporter,
    sqlalchemy_core_fetchall,
    sqlalchemy_pandas_read_sql_query,
)

import warnings

warnings.filterwarnings("ignore", category=UserWarning, message="pandas only supports SQLAlchemy")


method_map = {
    'pyodbc_pandas_read_sql_query': pyodbc_pandas_read_sql_query.run_pyodbc_pandas_read_sql_query,
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
    'sqlalchemy_pandas_read_sql_query': lambda conn, q: sqlalchemy_pandas_read_sql_query.run_sqlalchemy_pandas_read_sql_query_with_url(conn, q),
}

with open('extract_methods_mssql.yaml', 'r') as f:  # extract_methods_mssql
    config = yaml.safe_load(f)

sample_order = config.get('sample_order', 'serial')
sample_count = config.get('samples', 1)
all_results = []

if sample_order == 'serial':
    for method_name in config['methods']:
        method_func = method_map.get(method_name)
        if method_func:
            print(f"Running method: {method_name}")
            for i in range(sample_count):
                print(f"  Sample {i+1}/{sample_count}")
                monitor = ResourceMonitor(interval=config['monitoring']['interval'])
                monitor.start()
                elapsed, row_count = method_func(config['database']['conn_str'], config['database']['query'])
                monitor.stop()

                monitor_df = monitor.get_data()
                monitor_df.to_csv(f"results/{method_name}_monitor_sample_{i+1}.csv", index=False)

                all_results.append(
                    {
                        'method': method_name,
                        'sample': i + 1,
                        'elapsed_sec': elapsed,
                        'row_count': row_count,
                        'avg_cpu_percent': monitor_df['cpu_percent'].mean(),
                        'avg_mem_mb': monitor_df['mem_mb'].mean(),
                    }
                )

elif sample_order == 'mix':
    for i in range(sample_count):
        print(f"--- Sample round {i+1}/{sample_count} ---")
        for method_name in config['methods']:
            method_func = method_map.get(method_name)
            if method_func:
                print(f"  Running method: {method_name} (sample {i+1})")
                monitor = ResourceMonitor(interval=config['monitoring']['interval'])
                monitor.start()
                elapsed, row_count = method_func(config['database']['conn_str'], config['database']['query'])
                monitor.stop()

                monitor_df = monitor.get_data()
                monitor_df.to_csv(f"results/{method_name}_monitor_sample_{i+1}.csv", index=False)

                all_results.append(
                    {
                        'method': method_name,
                        'sample': i + 1,
                        'elapsed_sec': elapsed,
                        'row_count': row_count,
                        'avg_cpu_percent': monitor_df['cpu_percent'].mean(),
                        'avg_mem_mb': monitor_df['mem_mb'].mean(),
                    }
                )
else:
    raise ValueError(f"Invalid sample_order '{sample_order}' in config.yaml. Use 'serial' or 'mix'.")


summary_stats = []
df_all = pd.DataFrame(all_results)
df_all.to_csv("results/all_samples.csv", index=False)

for method_name, group in df_all.groupby('method'):
    summary_stats.append(
        {
            'method': method_name,
            'elapsed_min': group['elapsed_sec'].min(),
            'elapsed_max': group['elapsed_sec'].max(),
            'elapsed_avg': group['elapsed_sec'].mean(),
            'elapsed_median': group['elapsed_sec'].median(),
            'elapsed_mode': group['elapsed_sec'].mode()[0] if not group['elapsed_sec'].mode().empty else None,
            'cpu_avg': group['avg_cpu_percent'].mean(),
            'mem_avg': group['avg_mem_mb'].mean(),
        }
    )

df_summary = pd.DataFrame(summary_stats)
df_summary.to_csv("results/summary_stats.csv", index=False)
print(df_summary)

plt.figure(figsize=(18, 10))

for idx, (metric, ylabel) in enumerate(
    [
        ('elapsed_sec', 'Elapsed Time (sec)'),
        ('avg_cpu_percent', 'Average CPU Usage (%)'),
        ('avg_mem_mb', 'Average Memory (MB)'),
    ],
    start=1,
):
    plt.subplot(1, 3, idx)
    for method_name, group in df_all.groupby('method'):
        mean_val = group[metric].mean()
        min_val = group[metric].min()
        max_val = group[metric].max()
        median_val = group[metric].median()
        mode_val = group[metric].mode()[0] if not group[metric].mode().empty else None

        # Średnia z errorbarem
        plt.errorbar(x=[method_name], y=[mean_val], yerr=[[mean_val - min_val], [max_val - mean_val]], fmt='o', capsize=5, color='blue')

        # Mediana jako kwadrat
        plt.scatter(method_name, median_val, marker='s', color='green', label='Median' if idx == 1 else "")

        # Moda jako X jeśli jest
        if mode_val is not None:
            plt.scatter(method_name, mode_val, marker='x', color='red', label='Mode' if idx == 1 else "")

    plt.title(ylabel)
    plt.xticks(rotation=90)
    plt.grid(True)

# Dodaj wspólną legendę
handles = [
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', label='Mean'),
    plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='green', label='Median'),
    plt.Line2D([0], [0], marker='x', color='red', linestyle='None', label='Mode'),
]
plt.legend(handles=handles, bbox_to_anchor=(1.05, 1), loc='upper left')

plt.tight_layout()
plt.savefig('results/benchmark_summary.jpg')
plt.close()
