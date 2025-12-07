from pyspark.sql import SparkSession
from pyspark.sql import functions as f
from pyspark.sql.types import *
from utils.memory import measure_memory
from utils.timer import measure_time

DEFAULT_CRITICAL_COLUMNS = ['fare_amount', 'trip_distance', 'trip_duration_min']
CAST_COLUMNS = {'passenger_count': {'dtype': 'int', 'valid_range': (1, 9)}, 'RatecodeID': {'dtype': 'int', 'valid_range': (1, 6)}}

spark = SparkSession.builder.getOrCreate()

#Read data
def read_data(path):
    df = spark.read.parquet(path)
    return df

#Clean data
def clean_data(df, critical_columns):
    values_to_replace = [False, 'false', 'False']
    #Replace False value
    for c in df.columns:
        df = df.withColumn(c, f.when(f.col(c).isin(values_to_replace), None).otherwise(f.col(c)))
    #Drop duplicates
    df = df.distinct()
    #Drop columns with nulls in all columns
    df = df.na.drop(how='all')

    #Casts comprobations
    for col_name, props in CAST_COLUMNS.items():
        min_val, max_val = props['valid_range']
        df = df.withColumn(col_name, f.col(col_name).cast('int'))
        df = df.filter(f.col(col_name).isNotNull() & f.col(col_name).between(min_val, max_val))

    #Derived Columns
    df = df.withColumn(
        'trip_duration_min',
        (f.unix_timestamp(f.col('tpep_dropoff_datetime')) - f.unix_timestamp(f.col('tpep_pickup_datetime'))) / 60
    )
    df = df.withColumn('avg_speed_mph', f.col('trip_distance') / (f.col('trip_duration_min')) / 60 + 1e-6)

    df = df.na.drop(subset=critical_columns)

    return df

#Filter Data
def filter_data(df):
    df = df.filter((f.col('trip_distance') > 0.1) &
                   (f.col('fare_amount') > 2) &
                   (f.col('trip_duration_min').between(4, 240)))
    
    df = df.filter(f.col('extra') > 3.0)

    return df

#Group data and sort data
def group_sort_dataframe(df):

    grouped = df.groupBy('payment_type')\
        .agg(
            f.avg('fare_amount').alias('avg_fare'),
            f.count('VendorID').alias('total_trips'))\
        .orderBy(f.col('avg_fare').desc())

    return grouped

#Write output data
def write_data(df, output_path):
    df.write.parquet(output_path, mode='overwrite')

#run_pyspark_etl
@measure_memory
@measure_time
def run_etl_pyspark(input_path: str, output_path: str, critical_columns=None):
    critical_columns = critical_columns or DEFAULT_CRITICAL_COLUMNS 