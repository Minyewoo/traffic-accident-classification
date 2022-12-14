from os import getenv, path


class Config:
    def __init__(self) -> None:
        self.crawler_type = getenv('CRAWLER_TYPE', 'traffic_events')
        self.driver_path = getenv('DRIVER_PATH', path.join('.', 'gecko'))

        self.city_name = getenv('CITY_NAME', 'spb')

        self.traffic_url = getenv('TRAFFIC_URL', 'https://example.com')
        self.traffic_api_route = getenv('TRAFFIC_API_ROUTE', 'api')

        self.wforecast_url = getenv('WFORECAST_URL', 'https://example.com')
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

        self.redis_host = getenv('REDIS_HOST', 'localhost')
        self.redis_port = getenv('REDIS_PORT', '6379')

        self.rabbitmq_host = getenv('RABBITMQ_HOST', 'localhost')
        self.scheduler_exchange_name = getenv(
            'SCHEDULER_EXCHANGE_NAME', 'crawling_schedule')
