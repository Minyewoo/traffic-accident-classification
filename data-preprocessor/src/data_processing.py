from pyspark.sql import functions as F
from pyspark.sql.types import *

TRAFFIC_EVENTS_TARGET_COLUMNS = ['feedbacks', 'id', 'location', 'timestamp', 'city_name', 'scheduler_id']
TRAFFIC_EVENTS_DF_SCHEMA = schema = StructType([
    StructField('id', StringType(), True),
    StructField('latitude', DoubleType(), True),
    StructField('longitude', DoubleType(), True),
    StructField('dislikes', LongType(), True),
    StructField('likes', LongType(), True),
    StructField('date', TimestampType(), True),
    StructField('city_name', StringType(), True),
    StructField('scheduler_id', StringType(), True),
])
WHEATER_FORECAST_CACHE_PATH = '/tmp/weather_forecast.csv'
WHEATER_FORECAST_TARGET_COLUMNS = ['datetime', 'humidity', 'pressure', 'temperature', 'weather_type', 'wind_direction', 'wind_speed', 'city_name', 'scheduler_id']
WHEATER_FORECAST_DF_SCHEMA = schema = StructType([
    StructField('humidity', FloatType(), True),
    StructField('pressure', IntegerType(), True),
    StructField('temperature', IntegerType(), True),
    StructField('weather_type', StringType(), True),
    StructField('wind_direction', StringType(), True),
    StructField('wind_speed', FloatType(), True),
    StructField('date', TimestampType(), True),
    StructField('city_name', StringType(), True),
    StructField('scheduler_id', StringType(), True),
])

def convert_to_df(data, spark_session):
    data_rdd = spark_session.sparkContext.parallelize(data)
    data_df = spark_session.read.json(data_rdd)

    return data_df

def process_traffic_events(data, spark_session):
    if len(data) == 0:
        return spark_session.createDataFrame(
            spark_session.sparkContext.emptyRDD(), 
            TRAFFIC_EVENTS_DF_SCHEMA,
        )

    data_df = convert_to_df(data=data, spark_session=spark_session)
    data_df = data_df \
            .dropDuplicates(['id', ]) \
            .drop(*filter(lambda col_name: col_name not in TRAFFIC_EVENTS_TARGET_COLUMNS, data_df.columns)) \
            .withColumn('latitude', F.col('location.coordinates')[1]) \
            .withColumn('longitude', F.col('location.coordinates')[0]) \
            .drop('location') \
            .withColumn('dislikes', F.col('feedbacks.dislikes')) \
            .withColumn('likes', F.col('feedbacks.likes')) \
            .drop('feedbacks') \
            .withColumn('date', F.col('timestamp').cast('timestamp')) \
            .drop('timestamp')

    return data_df

def process_weather_forecast(data, spark_session):
    if len(data) == 0:
        return spark_session.createDataFrame(
            spark_session.sparkContext.emptyRDD(), 
            WHEATER_FORECAST_DF_SCHEMA,
        )

    data_df = convert_to_df(data=data, spark_session=spark_session)

    data_df = data_df \
            .drop(*filter(lambda col_name: col_name not in WHEATER_FORECAST_TARGET_COLUMNS, data_df.columns)) \
            .dropDuplicates(['scheduler_id', 'city_name']) \
            .withColumn('date', F.to_timestamp(F.col('datetime'), "yyyy-MM-dd'T'HH:mm:ss.SSSSSSVV")) \
            .drop('datetime') \
            .withColumn('humidity', F.regexp_replace(F.col('humidity'), '%', '').cast('float') / 100) \
            .withColumn('pressure', F.regexp_extract(F.col('pressure'), r'(\d+)', 1).cast('int')) \
            .withColumn('temperature', F.regexp_replace(F.col('temperature'), '−', '-').cast('int')) \
            .withColumn('wind_speed', F.regexp_replace(F.col('wind_speed'), ',', '.').cast('float'))

    return data_df

def get_joined_traffic_and_wheater_data(traffic_events_df, weather_forecast_df):
    time_interval_in_seconds = 900 # 15 minutes
    to_time_intervals = lambda col: (col.cast('long') / time_interval_in_seconds).cast('int')
    
    get_most_frequent_value = F.udf(lambda arr: max(set(arr), key = arr.count), 'string')

    weather_forecast_df = weather_forecast_df \
            .drop(F.col('scheduler_id')) \
            .withColumn('time_interval', to_time_intervals(F.col('date'))) \
            .groupby('time_interval', 'city_name') \
            .agg(
                F.avg(F.col('humidity')).alias('humidity'),
                F.avg(F.col('pressure')).alias('pressure'),
                F.avg(F.col('temperature')).alias('temperature'),
                get_most_frequent_value(F.collect_list(F.col('weather_type'))).alias('weather_type'),
                get_most_frequent_value(F.collect_list(F.col('wind_direction'))).alias('wind_direction'),
                F.avg(F.col('wind_speed')).alias('wind_speed'),
            )

    joined_df = traffic_events_df \
            .drop(F.col('scheduler_id')) \
            .join(weather_forecast_df, [
                to_time_intervals(traffic_events_df.date) == weather_forecast_df.time_interval,
                traffic_events_df.city_name == weather_forecast_df.city_name,
            ]) \
            .drop(weather_forecast_df.time_interval) \
            .drop(weather_forecast_df.city_name)

    return joined_df

def get_traffic_count_data(traffic_events_df, weather_forecast_df):
    time_tolerance_in_seconds = 300 # 5 minutes
    min_date = weather_forecast_df.agg({'date': 'min'}).collect()[0][0]

    traffic_events_df = traffic_events_df \
            .filter(F.col('date') + F.expr(f'INTERVAL {time_tolerance_in_seconds} seconds') > min_date) \
            .withColumn('event_flag', F.lit(1))

    traffic_count_df = weather_forecast_df \
            .join(traffic_events_df, [
                    traffic_events_df.city_name == weather_forecast_df.city_name,
                    traffic_events_df.scheduler_id == weather_forecast_df.scheduler_id,
                ], 'leftouter') \
            .drop(traffic_events_df.city_name) \
            .drop(traffic_events_df.scheduler_id) \
            .drop(traffic_events_df.date) \
            .groupby('city_name', 'scheduler_id') \
            .agg(
                F.sum(F.col('event_flag')).alias('crashes'),
                F.first(F.col('date')).alias('date'),
                F.first(F.col('humidity')).alias('humidity'),
                F.first(F.col('pressure')).alias('pressure'),
                F.first(F.col('temperature')).alias('temperature'),
                F.first(F.col('weather_type')).alias('weather_type'),
                F.first(F.col('wind_direction')).alias('wind_direction'),
                F.first(F.col('wind_speed')).alias('wind_speed'),
            ) \
            .drop(weather_forecast_df.scheduler_id) \
            .na.fill(value=0, subset=['crashes'])

    return traffic_count_df