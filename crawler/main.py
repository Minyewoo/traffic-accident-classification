from dotenv import dotenv_values
from traffic_crawler import TrafficCrawler
from weather_forecast_crawler import WeatherForecastCrawler
import json
import redis
from redis.commands.json.path import Path
import time
import pika

if __name__ == '__main__':
    config = dotenv_values('.env')

    traffic = TrafficCrawler(config['DRIVER_PATH'])
    traffic.go_to(config['TRAFFIC_URL'])
    events = traffic.find_events(config['TRAFFIC_API_ROUTE'], 'accident')
    traffic.finish()

    with open('forecast_field_selectors.json', 'r') as file:
        weather_forecast = WeatherForecastCrawler(
            config['DRIVER_PATH'], json.load(file)
        )
    weather_forecast.go_to(config['WFORECAST_URL'])
    forecast = weather_forecast.get_forecast()
    weather_forecast.finish()

    timestamp = time.time()
    events_id = f'events:{timestamp}'
    forecast_id = f'forecast:{timestamp}'

    redis_client = redis.Redis(host=config['REDIS_HOST'],
                               port=int(config['REDIS_PORT']), db=0)

    redis_client.json().set(events_id, Path.root_path(), events)
    redis_client.json().set(forecast_id, Path.root_path(), forecast)

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(config['RABBITMQ_HOST']))
    channel = connection.channel()
    channel.queue_declare(queue='crawled')

    crawled_ids = {'events': events_id, 'forecast': forecast_id}
    channel.basic_publish(exchange='',
                          routing_key='crawled',
                          body=json.dumps(crawled_ids))

    connection.close()
