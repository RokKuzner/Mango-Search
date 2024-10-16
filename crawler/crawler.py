from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from bs4 import BeautifulSoup

import re
import time

websites_to_crawl = ["https://www.selenium.dev/"] # WARNING: ONLY FOR DEVELOPMENT WITHOUT A DATABASE

class MangoCrawler():
    def __init__(self) -> None:
        # Global variables
        self.url_regex_pattern = re.compile(r"^(?:https?:\/\/)(?:www\.)?(?P<domain_name>[a-zA-Z0-9](?:[a-zA-Z0-9\-\.]{1,251}[a-zA-Z0-9])?)(?P<top_level_domain>\.[a-zA-Z0-9\-]{2,63})(?:(?:\:)(?P<port>\d{4}))?(?P<after>\/.*)?$")

        # Set up the options for chrome webdriver
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Create the driver
        self.driver = webdriver.Chrome(options=chrome_options)
  
    def get_next_website_to_crawl(self) -> str|None:
        if len(websites_to_crawl) == 0:
            return None
        return websites_to_crawl.pop(0)
    
    def filter_out_non_content(self, soup: BeautifulSoup) -> None:
        # Remove <header>, <footer>, <nav>, <aside> (common non-content sections)
        for tag in ['header', 'footer', 'nav', 'aside']:
            element = soup.find(tag)
            if element:
                element.decompose()  #  Removes the tag and its contents

    def extract_main_content(self, soup: BeautifulSoup) -> str:
        # Check for semantic tags: <article>, <main>, <section>
        content = ""
        for tag in ['article', 'main', 'section']:
            content_tag = soup.find(tag)
            if content_tag:
                content += content_tag.get_text(separator=' ', strip=True)

        # Look for <div> tags with content-heavy class names or IDs
        content_div = soup.find('div', attrs={'id': re.compile(r'(content|post|article|main)', re.I)})
        if content_div:
            content += content_div.get_text(separator=' ', strip=True)

        # Text Density Heuristics - Find blocks with a high text-to-tag ratio
        def calculate_text_density(tag):
            text_length = len(tag.get_text())
            tag_count = len(tag.find_all())
            return text_length / (tag_count + 1)  #  Avoid division by zero
        
        # Check the density of all <div> tags and select the highest density
        divs = soup.find_all('div')
        if divs:
            densest_div = max(divs, key=calculate_text_density)
            content += densest_div.get_text(separator=' ', strip=True)

        return content
    
    def crawl_webpage(self, webpage_url:str) -> None:
        self.driver.get(webpage_url)

        # Get the page source and parse it with BeautifulSoup
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Remove non-content sections
        self.filter_out_non_content(soup)

        # Extract main content
        main_content = self.extract_main_content(soup)

        # Get the page title
        page_title = self.driver.title

        print("Title:", page_title)

        print("Content:", main_content)

    def crawl_website(self, website_base_url:str):
        # Extract page domain
        domain_match = re.match(self.url_regex_pattern, website_base_url)
        page_domain = str(domain_match.group("domain_name")) + str(domain_match.group("top_level_domain"))

        print("Domain:", page_domain)

    def run(self):
        website_to_crawl_url = self.get_next_website_to_crawl()

        while True:
            if website_to_crawl_url == None:
                time.sleep(1)
                website_to_crawl_url = self.get_next_website_to_crawl()
                continue

MangoCrawler().run()