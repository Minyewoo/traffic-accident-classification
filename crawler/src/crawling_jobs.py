import json

from config import Config
from traffic_crawler import TrafficCrawler
from weather_forecast_crawler import WeatherForecastCrawler


def crawl_traffic_events():
    config = Config()

    traffic = TrafficCrawler(driver_path=config.driver_path)
    traffic.go_to(config.traffic_url)
    events = traffic.find_events(config.traffic_api_route, 'crash')
    traffic.finish()

    return events


def crawl_weather_forecast():
    config = Config()

    forecast_crawler = WeatherForecastCrawler(
        driver_path=config.driver_path,
        field_selector_mapping=json.loads(config.wforecast_field_selectors),
    )
    forecast_crawler.go_to(config.wforecast_url)
    forecast = forecast_crawler.get_forecast()
    forecast_crawler.finish()

    return forecast
