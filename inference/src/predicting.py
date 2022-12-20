import logging
import pyspark
from pyspark.sql import SparkSession, functions as F
from pyspark.ml.tuning import TrainValidationSplitModel
from config import Config
from pymongo import MongoClient
from datetime import  timedelta
from utils import (
    saved_model_exists,
)
from data_fetching import crawl_weather_forecasts
from data_processing import (
    prepare_for_inference,
    process_weather_forecast,
)

def predict_crashes(df, hdfs_url, old_model_path):
    model_path = f'{hdfs_url}/{old_model_path}'
    if not saved_model_exists(model_path):
        return 0
    
    model = TrainValidationSplitModel.load(model_path)
    return model.transform(df) \
        .withColumn('prediction', F.round(F.col('prediction')).cast('int'))

def save_to_mongo(config: Config, df):
    client = MongoClient(f'mongodb://{config.mongo_user}:{config.mongo_password}@{config.mongo_host}:{config.mongo_port}/')
    db = client[config.mongo_traffic_database]
    predictions = db[config.mongo_predictions_collection]

    for entry in df.rdd.collect():
        city = entry['city_name']
        crashes = entry['prediction']
        start_datetime = entry['date']
        end_datetime = start_datetime + timedelta(hours=1)

        predictions.insert_one({
            'city': city,
            'crashes': crashes,
            'startDate': start_datetime,
            'endDate': end_datetime,
        })

    client.close()

def predicting_job():
    config = Config()
    forecasts = crawl_weather_forecasts(config)
    logging.critical(f'Crawled for prediction:\n{forecasts}')
    spark_conf = pyspark.SparkConf()
    spark_conf.setAll(
        [
            ('spark.master', config.spark_master_url),
            ('spark.app.name', 'model-inference'),
            ('spark.submit.deployMode', 'client'),
            ('spark.driver.host', config.spark_driver_host),
            ('dfs.block.size', config.hdfs_block_size),
            ('spark.sql.sources.partitionOverwriteMode', 'dynamic'),
        ]
    )
    spark_session = SparkSession.builder \
            .config(conf=spark_conf) \
            .getOrCreate()
    df = process_weather_forecast(forecasts, spark_session)
    df = prepare_for_inference(df)
    df = predict_crashes(df, config.hdfs_url, config.traffic_best_model_saving_path)
    df.select('city_name', 'prediction').show()

    save_to_mongo(config, df)

    spark_session.stop()