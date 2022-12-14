import logging
import json
import time
import sys

import pyspark
import redis
import pika
from pyspark.sql import SparkSession
from config import Config
from data_etl_utils import (
    get_rabbit_queue_messages,
    get_redis_records,
    save_data_to_hdfs,
)
from data_processing import (
    process_traffic_events,
    process_weather_forecast,
    get_joined_traffic_and_wheater_data,
    get_traffic_count_data,
)

# while True:
#     pass

config = Config()

pika_parameters = pika.ConnectionParameters(
    host=config.rabbitmq_host,
    heartbeat=1800,
)
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

def start_spark_session(app_name):
    spark_conf = pyspark.SparkConf()
    spark_conf.setAll(
        [
            ('spark.master', config.spark_master_url),
            ('spark.app.name', app_name),
            ('spark.submit.deployMode', 'client'),
            ('spark.driver.host', config.spark_driver_host),
            ('dfs.block.size', config.hdfs_block_size),
            ('spark.sql.sources.partitionOverwriteMode', 'dynamic'),
            ('spark.ui.showConsoleProgress', 'false'),
        ]
    )
    spark_session = SparkSession.builder \
            .config(conf=spark_conf) \
            .getOrCreate()
    
    return spark_session


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
            records_ids=crawled_data_redis_ids.setdefault('weather_forecast', []),
            record_processor=lambda r: weather_forecast_accumulator(r, weather_forecast_crawled_data)
        )
        get_redis_records(
            client=redis_data_client,
            records_ids=crawled_data_redis_ids.setdefault('traffic_events', []),
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
    weather_data = record['data']
    weather_data['scheduler_id'] = record['scheduler_id']
    out_list.append(record['data'])

    return record

def traffic_events_accumulator(record, out_list, redis_client):
    events = record['data']['events']
    scheduler_id = record['scheduler_id']
    city_name = record['data']['city_name']

    for event in events:
        if redis_client.get(event['id']) is None:
            event['city_name'] = city_name
            event['scheduler_id'] = scheduler_id
            out_list.append(event)
            redis_client.set(event['id'], 'passed')

    return record

def process_crawled_data(data, spark_session):
    traffic_events_df = process_traffic_events(
        data=data['traffic_events'],
        spark_session=spark_session,
    )
    traffic_events_df.show(truncate=0, n=100)

    weather_forecast_df = process_weather_forecast(
        data=data['weather_forecast'],
        spark_session=spark_session,
    )
    weather_forecast_df.show(truncate=0)

    traffic_event_data = get_joined_traffic_and_wheater_data(
        traffic_events_df=traffic_events_df,
        weather_forecast_df=weather_forecast_df,
    )
    traffic_event_data.show()

    traffic_count_data  = get_traffic_count_data(
        traffic_events_df=traffic_events_df,
        weather_forecast_df=weather_forecast_df,
    )
    traffic_count_data.show()

    processed_data = {
        'traffic_event_data': traffic_event_data,
        'traffic_count_data': traffic_count_data,
    }

    return processed_data

def data_processing_callback(ch, method, properties, body):
    time.sleep(30)

    spark_session = start_spark_session(body)

    crawled_data = extract_crawled_data(
        pika_connection=pika_connection,
        redis_data_client=redis_crawled_data_client,
        redis_cache_client=redis_traffic_events_cache_client,
    )
    
    processed_data = process_crawled_data(data=crawled_data, spark_session=spark_session)

    save_data_to_hdfs(
        data=processed_data['traffic_event_data'],
        hdfs_url=config.hdfs_url,
        path=config.traffic_data_saving_path,
    )
    save_data_to_hdfs(
        data=processed_data['traffic_count_data'],
        hdfs_url=config.hdfs_url,
        path=config.traffic_count_data_saving_path,
    )

    spark_session.stop()
    
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
