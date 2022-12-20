from pyspark.sql import functions as F
from pyspark.sql.types import *
from pyspark.ml.feature import VectorAssembler, StringIndexer
from pyspark.ml import Pipeline

WHEATER_FORECAST_TARGET_COLUMNS = ['datetime', 'humidity', 'pressure', 'temperature', 'weather_type', 'wind_direction', 'wind_speed', 'city_name']
WHEATER_FORECAST_DF_SCHEMA = schema = StructType([
    StructField('humidity', FloatType(), True),
    StructField('pressure', IntegerType(), True),
    StructField('temperature', IntegerType(), True),
    StructField('weather_type', StringType(), True),
    StructField('wind_direction', StringType(), True),
    StructField('wind_speed', FloatType(), True),
    StructField('date', TimestampType(), True),
    StructField('city_name', StringType(), True),
])

def convert_to_df(forecasts, spark_session):
    columns = list(forecasts[0].keys())
    data = [list(entry.values()) for entry in forecasts]
    df = spark_session.sparkContext.parallelize(data).toDF(columns)
    return df

def process_weather_forecast(data, spark_session):
    if len(data) == 0:
        return spark_session.createDataFrame(
            spark_session.sparkContext.emptyRDD(), 
            WHEATER_FORECAST_DF_SCHEMA,
        )

    data_df = convert_to_df(data, spark_session=spark_session)
    data_df.show()
    data_df = data_df \
            .withColumn('date', F.to_timestamp(F.col('datetime'), "yyyy-MM-dd'T'HH:mm:ss.SSSSSS")) \
            .withColumn('humidity', F.regexp_replace(F.col('humidity'), '%', '').cast('float') / 100) \
            .withColumn('pressure', F.regexp_extract(F.col('pressure'), r'(\d+)', 1).cast('int')) \
            .withColumn('temperature', F.regexp_replace(F.col('temperature'), '−', '-').cast('int')) \
            .withColumn('wind_speed', F.regexp_replace(F.col('wind_speed'), ',', '.').cast('float')) \
            .withColumn('hour', F.date_format(F.col('date'), 'k').cast("int")) \
            .withColumn('month', F.date_format(F.col('date'), 'M').cast("int")) \
            .withColumn('weekday', F.date_format(F.col('date'), 'E')) \
            .drop('datetime')
    return data_df

def prepare_for_inference(df):
    processing_pipeline = Pipeline(
        stages=[
            StringIndexer(inputCol = 'city_name', outputCol = 'city_index', handleInvalid='skip'),
            StringIndexer(inputCol = 'weekday', outputCol = 'weekday_index', handleInvalid='skip'),
            StringIndexer(inputCol = 'weather_type', outputCol = 'weather_type_index', handleInvalid='skip'),
            StringIndexer(inputCol = 'wind_direction', outputCol = 'wind_direction_index', handleInvalid='skip'),
            VectorAssembler(
                inputCols=['city_index', 'humidity', 'pressure', 'temperature', 'wind_speed', 'hour', 'weekday_index', 'month', 'weather_type_index', 'wind_direction_index'],
                outputCol='features'
            )
        ]
    )

    return processing_pipeline \
        .fit(df) \
        .transform(df) \
        # .select(F.col('features'))