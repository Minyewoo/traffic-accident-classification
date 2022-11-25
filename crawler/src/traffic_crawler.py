import json
from seleniumwire.utils import decode
from selenium_crawler import SeleniumCrawler


class TrafficCrawler(SeleniumCrawler):
    def __init__(self, driver_path: str) -> None:
        super().__init__(driver_path)

    def find_events(self, api_route: str, event_type: str):
        response = self.driver.wait_for_request(api_route).response

        predecoded_data = decode(response.body, response.headers.get(
            'Content-Encoding', 'identity'))
        entries = json.loads(predecoded_data.decode("utf8"))

        events = list(
            filter(lambda entry: entry['type'] == event_type, entries))

        return events
