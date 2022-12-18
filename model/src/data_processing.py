from pyspark.sql import functions as F
from pyspark.ml.feature import VectorAssembler, StringIndexer
from pyspark.ml import Pipeline

def load_data(spark_session, hdfs_url, traffic_count_data_saving_path):
    get_most_frequent_value = F.udf(lambda arr: max(set(arr), key = arr.count), 'string')
    return spark_session.read.options(header='True', inferSchema='True', delimiter=',') \
        .csv( f'{hdfs_url}/{traffic_count_data_saving_path}') \
        .withColumn('hour', F.date_format(F.col('date'), 'k').cast("int")) \
        .withColumn('month', F.date_format(F.col('date'), 'M').cast("int")) \
        .withColumn('weekday', F.date_format(F.col('date'), 'E')) \
        .withColumn('grouping_day', F.date_format(F.col('date'), 'D').cast("int")) \
        .drop('date') \
        .groupBy(['city_name', 'grouping_day', 'hour']) \
        .agg(
            F.sum('crashes').alias('crashes'), \
            F.avg('humidity').alias('humidity'), \
            F.avg('pressure').alias('pressure'), \
            F.avg('temperature').alias('temperature'), \
            F.avg('wind_speed').alias('wind_speed'), \
            F.first('month').alias('month'), \
            F.first('weekday').alias('weekday'), \
            get_most_frequent_value(F.collect_list(F.col('weather_type'))).alias('weather_type'), \
            get_most_frequent_value(F.collect_list(F.col('wind_direction'))).alias('wind_direction'), \
        ) \
        .drop('grouping_day')

def prepare_for_training(df, train_ratio=0.8):
    processing_pipeline = Pipeline(
        stages=[
            StringIndexer(inputCol = 'city_name', outputCol = 'city_index'),
            StringIndexer(inputCol = 'weekday', outputCol = 'weekday_index'),
            StringIndexer(inputCol = 'weather_type', outputCol = 'weather_type_index'),
            StringIndexer(inputCol = 'wind_direction', outputCol = 'wind_direction_index'),
            VectorAssembler(
                inputCols=['city_index', 'humidity', 'pressure', 'temperature', 'wind_speed', 'hour', 'weekday_index', 'month', 'weather_type_index', 'wind_direction_index'],
                outputCol='features'
            )
        ]
    )

    return processing_pipeline \
        .fit(df) \
        .transform(df) \
        .select(F.col('features'), F.col('crashes').alias('label')) \
        .randomSplit([train_ratio, 1 - train_ratio], seed=2022)