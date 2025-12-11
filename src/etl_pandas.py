import pandas as pd
from utils.measure import measure_time_and_memory


DEFAULT_CRITICAL_COLUMNS = ['fare_amount', 'trip_distance', 'trip_duration_min']
CAST_COLUMNS = {'passenger_count': {'dtype': 'Int64', 'valid_range': (1, 9)}, 'RatecodeID': {'dtype': 'Int64', 'valid_range': (1, 6)}}

#Read dataset
def read_data(path):
    df = pd.read_parquet(path)
    return df

#Clean data
def clean_data(df, critical_columns):
    #Replace False values
    df = df.replace([False, 'false', 'False'], pd.NA)
    #Drop duplicates
    df = df.drop_duplicates()
    #Drop columns with nulls in all columns
    df = df.dropna(how='all')

    #Casts comprobations
    for col, props in CAST_COLUMNS.items():
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=[col])
        min_val, max_val = props['valid_range']
        df = df[df[col].between(min_val, max_val)]
    
    #Derived Columns
    df['trip_duration_min'] = (
        (df['tpep_dropoff_datetime'] - df['tpep_pickup_datetime']).dt.total_seconds() / 60
    )
    df['avg_speed_mph'] = df['trip_distance'] / (df['trip_duration_min'] / 60 + 1e-6)

    #Drop na in critical columns
    df = df.dropna(subset=critical_columns)

    return df

#Filter Data
def filter_data(df):
    df = df[(df['trip_distance'] > 0.1) &
            (df['fare_amount'] > 2) &
            (df['trip_duration_min'].between(4, 240))]
    
    df = df[df['extra'] >= 3.0]

    return df
    
#Group data and sort data
def group_sort_dataframe(df):

    grouped = df.groupby('payment_type').agg(
        avg_fare=('fare_amount', 'mean'),
        total_trips=('VendorID', 'count')
    ).reset_index()

    grouped = grouped.sort_values('avg_fare', ascending=False)

    return grouped

#Write output data
def write_data(df, output_path):
    df.to_parquet(output_path, index=False)

#run_pandas_etl
@measure_time_and_memory
def run_etl_pandas(input_path: str, output_path: str, critical_columns=None):
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