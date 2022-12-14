from datetime import datetime
from zoneinfo import ZoneInfo
from selenium_crawler import SeleniumCrawler
from selenium.webdriver.common.by import By
import time


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

        timezone = ZoneInfo('Europe/Moscow')
        forecast['datetime'] = datetime.now(tz=timezone).isoformat()

        return forecast
