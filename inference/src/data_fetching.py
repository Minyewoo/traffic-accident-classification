from datetime import datetime
import json
from selenium.webdriver.common.by import By
from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options
import time
from config import Config

def crawl_weather_forecasts(config: Config):
    forecasts = []
    forecast_crawler = WeatherForecastCrawler(
        driver_path=config.driver_path,
        field_selector_mapping=json.loads(config.wforecast_field_selectors),
    )
    for city_name, url in config.forecast_urls.items():
        forecast_crawler.go_to(url)
        forecast = forecast_crawler.get_forecast()
        forecast['city_name'] = city_name
        forecasts.append(forecast)
    forecast_crawler.finish()
    return forecasts


class SeleniumCrawler:
    def __init__(self, driver_path: str) -> None:
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(
            options=options, executable_path=driver_path)

    def go_to(self, request_url: str):
        self.driver.get(request_url)

    def finish(self):
        self.driver.quit()

class WeatherForecastCrawler(SeleniumCrawler):
    def __init__(self, driver_path: str, field_selector_mapping: dict) -> None:
        self.field_selector_mapping = field_selector_mapping
        super().__init__(driver_path)

    def get_forecast(self):
        time.sleep(5)
        forecast = {}

        for field_name, params in self.field_selector_mapping.items():
            try:
                content = self.driver.find_element(
                    By.CSS_SELECTOR, params['selector'])
                forecast[field_name] = content.text
            except:
                forecast[field_name] = params['default']

        forecast['datetime'] = datetime.now().isoformat()

        return forecast
