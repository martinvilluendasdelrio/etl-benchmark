import polars as pl
from utils.memory import measure_memory
from utils.timer import measure_time


DEFAULT_CRITICAL_COLUMNS = ['fare_amount', 'trip_distance', 'trip_duration_min']
CAST_COLUMNS = {'passenger_count': {'dtype': 'Int64', 'valid_range': (1, 9)}, 'RatecodeID': {'dtype': 'Int64', 'valid_range': (1, 6)}}

#Read dataset
def read_data(path):
    df = pl.read_parquet(path)
    return df

#Clean data
def clean_data(df, critical_columns):
    #Replace False values
    df = df.replace([False, 'false', 'False'], pl.lit(None))
    #Drop duplicates
    df = df.unique()
    #Drop columns with nulls in all columns
    df = df.drop_nulls(how='all')

    #Casts comprobations
    for col, props in CAST_COLUMNS.items():
        min_val, max_val = props['valid_range']

        # Convertir a número (Int64, coercion a None si falla)
        df = df.with_columns(
            pl.col(col).cast(pl.Int64, strict=False)  # equivalente a pd.to_numeric(errors='coerce')
        )

        # Filtrar nulos y valores fuera del rango
        df = df.filter(
            pl.col(col).is_not_null() & pl.col(col).is_between(min_val, max_val)
        )
    
    #Derived Columns
    df = df.with_columns([
        # Duración del viaje en minutos
        ((pl.col("tpep_dropoff_datetime") - pl.col("tpep_pickup_datetime")).dt.seconds() / 60).alias("trip_duration_min"),
    
        # Velocidad promedio en mph
        (pl.col("trip_distance") / ( ((pl.col("tpep_dropoff_datetime") - pl.col("tpep_pickup_datetime")).dt.seconds() / 60) / 60 + 1e-6 )).alias("avg_speed_mph")
    ])

    #Drop na in critical columns
    df = df.drop_nulls(subset=critical_columns)

    return df

#Filter Data
def filter_data(df):
    df = df.filter(pl.col('trip_distance') > 0.1)
    df = df.filter(pl.col('fare_amount') > 2)
    df = df.filter(pl.col('trip_duration_min').is_between(4, 240))
    df = df.filter(pl.col('extra') >= 3.0)

    return df

#Group data and sort data
def group_sort_dataframe(df):
    grouped = df.lazy().group_by('payment_type').agg(
        avg_fare=('fare_amount', 'mean'),
        total_trips=('VendorID', 'count')
    )

    grouped = grouped.sort('avg_fare', ascending=False)

    return grouped

#Write data
def write_data(df, output_path):
    df.write_parquet(output_path)

#run_polars_etl
@measure_memory
@measure_time
def run_etl_polars(input_path: str, output_path:str, critical_columns=None):
    critical_columns = critical_columns or DEFAULT_CRITICAL_COLUMNS