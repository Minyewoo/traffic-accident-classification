import json
import time
from random import randint

import pika
import redis
import schedule
from config import Config
from dotenv import load_dotenv
from redis.commands.json.path import Path
from traffic_crawler import TrafficCrawler
from weather_forecast_crawler import WeatherForecastCrawler


def crawling_job():
    time.sleep(randint(1, 5) * 60)

    config = Config()

    traffic = TrafficCrawler(driver_path=config.driver_path)
    traffic.go_to(config.traffic_url)
    events = traffic.find_events(config.traffic_api_route, 'accident')
    traffic.finish()

    weather_forecast = WeatherForecastCrawler(
        driver_path=config.driver_path,
        field_selector_mapping=json.loads(config.wforecast_field_selectors),
    )
    weather_forecast.go_to(config.wforecast_url)
    forecast = weather_forecast.get_forecast()
    weather_forecast.finish()

    timestamp = time.time()
    events_id = f'events:{timestamp}'
    forecast_id = f'forecast:{timestamp}'

    redis_client = redis.Redis(host=config.redis_host,
                               port=int(config.redis_port), db=0)

    redis_client.json().set(events_id, Path.root_path(), events)
    redis_client.json().set(forecast_id, Path.root_path(), forecast)

    redis_client.close()

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(config.rabbitmq_host))
    channel = connection.channel()
    channel.queue_declare(queue='crawled')

    crawled_ids = {'events': events_id, 'forecast': forecast_id}
    channel.basic_publish(exchange='',
                          routing_key='crawled',
                          body=json.dumps(crawled_ids))

    connection.close()


if __name__ == '__main__':
    schedule.every().hour.do(crawling_job)

    while 1:
        n = schedule.idle_seconds()
        if n is None:
            # no more jobs
            break
        if n > 0:
            # sleep exactly the right amount of time
            time.sleep(n)
        schedule.run_pending()
