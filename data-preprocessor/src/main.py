import logging
import json
import sys

import pyspark
import redis
import pika
from pyspark.sql import SparkSession
from config import Config
from data_extracting_utils import get_rabbit_queue_messages, get_redis_records
from data_processing import process_traffic_events, process_weather_forecast, join_traffic_and_wheater_data


config = Config()

pika_parameters = pika.ConnectionParameters(host=config.rabbitmq_host)
pika_connection = pika.BlockingConnection(parameters=pika_parameters)
pika_channel = pika_connection.channel()

redis_crawled_data_client = redis.Redis(
    host=config.redis_host,
    port=int(config.redis_port),
    db=0,
)
redis_traffic_events_cache_client = redis.Redis(
    host=config.redis_host,
    port=int(config.redis_port),
    db=1,
)

spark_conf = pyspark.SparkConf()
spark_conf.setAll(
    [
        ('spark.master', config.spark_master_url),
        ('spark.app.name', 'data-preprocessor'),
        ('spark.submit.deployMode', 'client'),
        ('spark.driver.host', config.spark_driver_host),
    ]
)
spark_session = SparkSession.builder \
        .config(conf=spark_conf) \
        .getOrCreate()


def extract_crawled_data(pika_connection, redis_data_client, redis_cache_client):
    crawled_data_redis_ids = {}
    weather_forecast_crawled_data = [] 
    traffic_events_crawled_data = []

    msgs = get_rabbit_queue_messages(
        connection=pika_connection,
        queue_name=config.crawled_queue_name,
        message_processor=lambda msg: message_sorter(json.loads(msg), crawled_data_redis_ids)
    )
    
    if msgs is not None:
        get_redis_records(
            client=redis_data_client,
            records_ids=crawled_data_redis_ids['weather_forecast'],
            record_processor=lambda r: weather_forecast_accumulator(r, weather_forecast_crawled_data)
        )
        get_redis_records(
            client=redis_data_client,
            records_ids=crawled_data_redis_ids['traffic_events'],
            record_processor=lambda r: traffic_events_accumulator(r, traffic_events_crawled_data, redis_cache_client)
        )

    crawled_data = {
        'weather_forecast': weather_forecast_crawled_data,
        'traffic_events': traffic_events_crawled_data,
    }

    return crawled_data

def message_sorter(message, out_dict):
    cache_id = message['cache_id']
    crawler_type = message['crawler_type']
    out_dict.setdefault(crawler_type, []).append(cache_id)

    return message

def weather_forecast_accumulator(record, out_list):
    out_list.append(record['data'])

    return record

def traffic_events_accumulator(record, out_list, redis_client):
    events = record['data']

    for event in events:
        if redis_client.get(event['id']) is None:
            out_list.append(event)
            redis_client.set(event['id'], 'passed')

    return record

def process_crawled_data(data, spark_session):
    traffic_events_df = process_traffic_events(
        data=data['traffic_events'],
        spark_session=spark_session,
    )

    weather_forecast_df = process_weather_forecast(
        data=data['weather_forecast'],
        spark_session=spark_session,
    )

    processed_data = join_traffic_and_wheater_data(
        traffic_events_df=traffic_events_df,
        weather_forecast_df=weather_forecast_df
    )
    
    return processed_data

def save_crawled_data(data):
    data.write.csv(
        f'{config.hdfs_url}/{config.data_saving_path}',
        mode='append',
        header=True,
    )

def data_processing_callback(ch, method, properties, body):
    crawled_data = extract_crawled_data(
        pika_connection=pika_connection,
        redis_data_client=redis_crawled_data_client,
        redis_cache_client=redis_traffic_events_cache_client,
    )
    
    processed_data = process_crawled_data(data=crawled_data, spark_session=spark_session)

    save_crawled_data(processed_data)

    logging.critical(f'Processed: {body}')


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.CRITICAL)

    pika_channel.exchange_declare(
        exchange=config.processing_scheduler_exchange_name, exchange_type='fanout')

    queue_info = pika_channel.queue_declare(queue='', exclusive=True)
    queue_name = queue_info.method.queue

    pika_channel.queue_bind(
        exchange=config.processing_scheduler_exchange_name, queue=queue_name)

    pika_channel.basic_consume(
        queue=queue_name, on_message_callback=data_processing_callback, auto_ack=True)

    pika_channel.start_consuming()
