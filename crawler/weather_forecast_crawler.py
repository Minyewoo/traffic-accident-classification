from datetime import datetime
from zoneinfo import ZoneInfo
from selenium_crawler import SeleniumCrawler
from selenium.webdriver.common.by import By
from dotenv import dotenv_values
import time
import json


class WeatherForecastCrawler(SeleniumCrawler):
    def __init__(self, driver_path: str, field_selector_mapping: dict) -> None:
        self.field_selector_mapping = field_selector_mapping
        super().__init__(driver_path)

    def get_forecast(self):
        time.sleep(5)
        forecast = {}

        for field_name, selector in self.field_selector_mapping.items():
            content = self.driver.find_element(By.CSS_SELECTOR, selector)
            forecast[field_name] = content.text

        timezone = ZoneInfo('Europe/Moscow')
        forecast['datetime'] = datetime.now(tz=timezone).isoformat()

        return forecast


# config = dotenv_values('.env')
# with open('forecast_field_selectors.json', 'r') as file:
#     weather_forecast = WeatherForecastCrawler(
#         config['DRIVER_PATH'], json.load(file)
#     )
# weather_forecast.go_to(config['WFORECAST_URL'])
# print(weather_forecast.get_forecast())

# weather_forecast.finish()
