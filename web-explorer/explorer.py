from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import selenium.common.exceptions

from fake_useragent import UserAgent

from urllib.parse import urlparse, urlunparse
import requests
import re
import urllib.parse

class MangoExplorer():
    def __init__(self) -> None:
        # Global variables
        self.url_regex_pattern = re.compile(r"^(?:https?:\/\/)(?:www\.)?(?P<domain_name>[a-zA-Z0-9](?:[a-zA-Z0-9\-\.]{0,251}[a-zA-Z0-9])?)(?P<top_level_domain>\.[a-zA-Z]{2,63})(?::(?P<port>\d{1,5}))?(?P<subpages>\/[^\?#]*)?(?P<arguments>\?[^#]*)?(?P<fragment>#.*)?$")
        self.db_interface_url = 'http://db-interface:5000'

        #Initialize the state of the explorer
        self.is_active = False

        # Set up the options for chrome webdriver
        self.user_agent = UserAgent()
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--lang=en-US")
        chrome_options.add_argument(f"--user-agent={self.user_agent.random}")

        # Create the driver
        self.driver = webdriver.Chrome(options=chrome_options)

    def clean_strip_url(self, url:str) -> str:
        """Cleans and strips a url. Example: "https://www.google.com/search?q=lol" -> "https://www.google.com/"

        Keyword arguments:
        url -- the url to clean and strip
        Return: stripped and cleaned url
        """

        parsed_url = urllib.parse.urlparse(url)
        clean_url = urllib.parse.urlunparse((parsed_url.scheme, parsed_url.netloc, "", "", "", "")) + "/"

        return clean_url
    
    def add_website_to_index(self, url:str) -> None:
        response = requests.post(f'{self.db_interface_url}/request_website_index', json={"url":url})

    def website_in_index_quee(self, url:str) -> bool:
        response = requests.post(f'{self.db_interface_url}/check_website_in_index_quee', json={"url":url})
        return response.json()["data"]
    
    def get_links(self, url:str):
        self.driver.get(url)

        link_elements = self.driver.find_elements(By.TAG_NAME, "a")

        return [element.get_attribute("href") for element in link_elements]

    def run(self, website_url:str):
        #Set the state to active
        self.is_active = True

        links = self.get_links(website_url)

        #Add links to the index quee
        for link in links:
            # Clean the link
            clean_link = self.clean_strip_url(link)

            # Check if link is valid, points to a different website and not allready added to the indexing quee
            if ( clean_link ) and ( not clean_link.startswith(website_url) ) and ( re.match(self.url_regex_pattern, clean_link) ) and ( not self.website_in_index_quee(clean_link) ):
                self.add_website_to_index(clean_link)

        self.driver.quit()
        self.is_active = False