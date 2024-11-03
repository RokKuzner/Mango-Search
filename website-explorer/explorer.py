from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import selenium.common.exceptions

from fake_useragent import UserAgent
from urllib.parse import urlparse, urlunparse

import re
import requests

class MangoExplorer():
    def __init__(self) -> None:
        # Global variables
        self.url_regex_pattern = re.compile(r"^(?:https?:\/\/)(?:www\.)?(?P<domain_name>[a-zA-Z0-9](?:[a-zA-Z0-9\-\.]{0,251}[a-zA-Z0-9])?)(?P<top_level_domain>\.[a-zA-Z]{2,63})(?::(?P<port>\d{1,5}))?(?P<subpages>\/[^\?#]*)?(?P<arguments>\?[^#]*)?(?P<fragment>#.*)?$")
        self.to_explore = ["https://en.wikipedia.org/wiki/List_of_most-visited_websites"]

        # Set up the options for chrome webdriver
        self.user_agent = UserAgent()
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"user-agent={self.user_agent.random}")

        # Create the driver
        self.driver = webdriver.Chrome(options=chrome_options)

    def explore(self) -> None:
        while self.to_explore:
            # Get the next URL to explore
            url = self.to_explore.pop(0)

            # Visit the URL
            try:
                self.driver.get(url)
            except selenium.common.exceptions.WebDriverException:
                continue

            #TODO: continue
            
