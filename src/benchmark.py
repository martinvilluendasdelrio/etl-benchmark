from etl_pandas import run_etl_pandas
from etl_polars import run_etl_polars
from etl_pyspark import run_etl_pyspark
import statistics

READ_PATH = "../data/raw/yellow_tripdata_2022-12.parquet"
WRITE_PATH = "../data/processed/"


# Número de repeticiones de cada ETL
N_REPEATS = 5

# Lista de ETLs a testear
ETL_ENGINES = [
    ("pandas", run_etl_pandas, "output_pandas.parquet"),
    ("polars", run_etl_polars, "output_polars.parquet"),
    ("pyspark", run_etl_pyspark, "output_spark.parquet"),
]
def run_benchmark():
    results_summary = []

    for engine_name, run_func, output_file in ETL_ENGINES:
        print(f"\n=== Running {engine_name.upper()} ETL ({N_REPEATS} repetitions) ===")

        times = []
        memories = []

        for i in range(N_REPEATS):
            print(f"Run {i+1}/{N_REPEATS}...")
            _, t, m = run_func(
                str(READ_PATH),
                str(WRITE_PATH / output_file)
            )
            times.append(t)
            memories.append(m)

        # Calculamos media y desviación estándar
        mean_time = statistics.mean(times)
        std_time = statistics.stdev(times)
        mean_mem = statistics.mean(memories)
        std_mem = statistics.stdev(memories)

        results_summary.append({
            "engine": engine_name,
            "mean_time": mean_time,
            "std_time": std_time,
            "mean_mem": mean_mem,
            "std_mem": std_mem
        })

    print_results(results_summary)


def print_results(summary):
    print("\n\n===== BENCHMARK RESULTS =====\n")
    print(f"{'Engine':<10} {'Time(s)':<20} {'Memory(MB)':<20}")
    print("-" * 50)

    for r in summary:
        print(f"{r['engine']:<10} "
              f"{r['mean_time']:.2f} ± {r['std_time']:.2f}   "
              f"{r['mean_mem']:.2f} ± {r['std_mem']:.2f}")

    print("\n=============================\n")


if __name__ == "__main__":
    run_benchmark()