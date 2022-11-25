import sys
import json
import logging

import pika
import redis
from config import Config
from redis.commands.json.path import Path
from crawling_jobs import crawl_traffic_events, crawl_weather_forecast

config = Config()

connection = pika.BlockingConnection(
    pika.ConnectionParameters(config.rabbitmq_host))


def save_to_redis(id, crawler_type, crawler_data):
    redis_client = redis.Redis(host=config.redis_host,
                               port=int(config.redis_port), db=0)

    persisting_data = {
        'scheduler_id': id,
        'crawler_type': crawler_type,
        'data': crawler_data,
    }

    data_id = f'{crawler_type}:{id}'
    redis_client.json().set(data_id, Path.root_path(), persisting_data)

    redis_client.close()

    return data_id


def cached_crawl(schedule_id, crawler_type, crawler_fn):
    crawled_data = crawler_fn()
    data_id = save_to_redis(schedule_id, crawler_type, crawled_data)

    crawled_info = {'schedule_id': schedule_id,
                    'cache_id': data_id, 'crawler_type': crawler_type}

    return crawled_info


def crawler_callback(body, crawler_type, crawler_fn):
    scheduler_data = json.loads(body)
    schedule_id = scheduler_data['schedule_id']

    crawled_info = cached_crawl(schedule_id, crawler_type, crawler_fn)

    message = json.dumps(crawled_info)

    channel = connection.channel()

    channel.queue_declare(queue='crawled')

    channel.basic_publish(exchange='',
                          routing_key='crawled',
                          body=message)

    logging.critical(f' Crawled {message}')

    channel.close()


def traffic_events_callback(ch, method, properties, body):
    crawler_callback(body, 'traffic_events', crawl_traffic_events)


def weather_forecast_callback(ch, method, properties, body):
    crawler_callback(body, 'weather_forecast', crawl_weather_forecast)


callbacks_mapping = {
    'traffic_events': traffic_events_callback,
    'weather_forecast': weather_forecast_callback,
}


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.CRITICAL)
    selected_crawler_callback = callbacks_mapping[config.crawler_type]

    channel = connection.channel()

    channel.exchange_declare(
        exchange=config.scheduler_exchange_name, exchange_type='fanout')

    queue_info = channel.queue_declare(queue='', exclusive=True)
    queue_name = queue_info.method.queue

    channel.queue_bind(
        exchange=config.scheduler_exchange_name, queue=queue_name)

    channel.basic_consume(
        queue=queue_name, on_message_callback=selected_crawler_callback, auto_ack=True)

    channel.start_consuming()
