from ipaddress import IPv4Address, IPv4Network
import json
from subprocess import check_output
from os import getenv, path

class Config:
    def __init__(self) -> None:
        self.mongo_host = getenv('MONGODB_HOST', 'mongo')
        self.mongo_port = getenv('MONGODB_PORT', '27017')
        self.mongo_user = getenv('MONGODB_USERNAME', 'root')
        self.mongo_password = getenv('MONGODB_PASSWORD', 'kavo')
        self.mongo_traffic_database = getenv('MONGODB_DATABASE', 'traffic')
        self.mongo_predictions_collection = getenv('MONGODB_PREDICTIONS_COLLECTION', 'predictions')

        self.rabbitmq_host = getenv('RABBITMQ_HOST', 'rabbitmq')

        self.hdfs_url = getenv('HDFS_URL', 'hdfs://hdfs-namenode:8020')
        self.traffic_count_data_saving_path = getenv('TRAFFIC_COUNT_DATA_SAVING_PATH', 'processed/data-traffic-count.csv')
        self.traffic_best_model_saving_path = getenv('TRAFFIC_BEST_MODEL_SAVING_PATH', 'weights/best_weights')
        self.hdfs_block_size = getenv('HDFS_BLOCK_SIZE', '1048576')

        self.inference_scheduler_exchange_name = getenv(
            'INFERENCE_SCHEDULER_EXCHANGE_NAME', 'inference_schedule')

        self.driver_path = getenv('DRIVER_PATH', path.join('.', 'gecko'))
        self.forecast_urls = json.loads(getenv('WFORECAST_URLS', '{"msc":"https://google.com","spb":"https://google.com"}'))
        self.wforecast_field_selectors = getenv(
            'WFORECAST_FIELD_SELECTORS',
            '{"temperature":"div.temperature",\
            "weather_type":"div.weather_type",\
            "temperature_feelings":"div.temperature_feelings",\
            "wind_speed":"div.wind-speed",\
            "wind_direction":"div.wind_direction",\
            "humidity":"div.humidity",\
            "pressure":"div.pressure",\
            "water_temperature":"div.water_temperature"}'
        )

        self.spark_master_url = getenv('SPARK_MASTER_URL', 'spark://spark:7077')
        [ self.spark_driver_host ] = filter(
            lambda ip: IPv4Address(ip) in IPv4Network(getenv('SPARK_SUBNET')),
            check_output(['hostname', '-i']).decode(encoding='utf-8').strip().split()
        )
