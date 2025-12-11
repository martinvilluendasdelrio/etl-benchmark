import polars as pl
from utils.measure import measure_time_and_memory


DEFAULT_CRITICAL_COLUMNS = ['fare_amount', 'trip_distance', 'trip_duration_min']
CAST_COLUMNS = {'passenger_count': {'dtype': 'Int64', 'valid_range': (1, 9)}, 'RatecodeID': {'dtype': 'Int64', 'valid_range': (1, 6)}}

#Read dataset
def read_data(path):
    df = pl.read_parquet(path)
    return df

#Clean data
def clean_data(df, critical_columns):
    #Replace False values
    for col in df.columns:
        if df[col].dtype in [pl.Boolean, pl.Utf8]:
            df = df.with_columns(
                pl.when(
                    (pl.col(col) == False) | (pl.col(col).cast(pl.Utf8).str.to_lowercase() == "false")
                )
                .then(None)
                .otherwise(pl.col(col))
                .alias(col)
            )

    #Drop duplicates
    df = df.unique()
    #Drop columns with nulls in all columns
    df = df.select([pl.col(c) for c in df.columns if df[c].null_count() < df.height])


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
    
    # Derived Columns
    df = df.with_columns([
        # Duración del viaje en minutos
        ((pl.col("tpep_dropoff_datetime").cast(pl.Int64) - pl.col("tpep_pickup_datetime").cast(pl.Int64)) / 60).alias("trip_duration_min"),

        # Velocidad promedio en mph
        (pl.col("trip_distance") / (
            ((pl.col("tpep_dropoff_datetime").cast(pl.Int64) - pl.col("tpep_pickup_datetime").cast(pl.Int64)) / 60) / 60 + 1e-6
        )).alias("avg_speed_mph")
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

    grouped = grouped.sort(
        by=['avg_fare'],       # columnas a ordenar
        descending=[True]      # True para descendente, False para ascendente
    )

    return grouped

#Write data
def write_data(df, output_path):
    df.collect().write_parquet(output_path)

#run_polars_etl
@measure_time_and_memory
def run_etl_polars(input_path: str, output_path:str, critical_columns=None):
    critical_columns = critical_columns or DEFAULT_CRITICAL_COLUMNS

    #Use read_data function (returns DataFrame)
    df = read_data(input_path)
    #Use clean_data funcition (returns DataFrame)
    df_clean = clean_data(df, critical_columns)
    #Use filter_data function (returns DataFrame)
    df_filtered = filter_data(df_clean)
    #Use group_data function (returns DataFrame)
    grouped = group_sort_dataframe(df_filtered)
    #Use write_dataframe (returns DataFrame)
    write_data(grouped, output_path)
    grouped.head(100)
    return grouped