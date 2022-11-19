from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options


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
