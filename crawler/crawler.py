from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup
from keybert import KeyBERT

import re
import requests
import time

websites_to_crawl = ["https://www.selenium.dev/"] # WARNING: ONLY FOR DEVELOPMENT WITHOUT A DATABASE

class MangoCrawler():
    def __init__(self) -> None:
        # Global variables
        self.url_regex_pattern = re.compile(r"^(?:https?:\/\/)(?:www\.)?(?P<domain_name>[a-zA-Z0-9](?:[a-zA-Z0-9\-\.]{1,251}[a-zA-Z0-9])?)(?P<top_level_domain>\.[a-zA-Z0-9\-]{2,63})(?:(?:\:)(?P<port>\d{4}))?(?P<after>\/.*)?$")
        self.sitemap_in_robots_regex_pattern = re.compile(r"(?:sitemap)(?::)(?: )(?P<sitemap_url>(?:https?:\/\/)(?:www\.)?(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-\.]{1,251}[a-zA-Z0-9])?)(?:\.[a-zA-Z0-9\-]{2,63})(?:(?:\:)(\d{4}))?(?:\/.*))", flags=re.M|re.I)
        self.sitemap_locations = ["/sitemap.xml",  "/sitemap-index.xml", "/sitemap/sitemap.xml", "/sitemapindex.xml", "/sitemap/index.xml", "/sitemap1.xml"]

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
    
    def crawl_webpage(self, webpage_url:str) -> dict:
        self.driver.get(webpage_url)

        # Get the page source and parse it with BeautifulSoup
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Remove non-content sections
        self.filter_out_non_content(soup)

        # Extract main content
        main_content = self.extract_main_content(soup)

        #Extract keywords
        kw_model = KeyBERT()
        keywords = kw_model.extract_keywords(main_content, keyphrase_ngram_range=(1, 2), stop_words=None, top_n=10)
        keywords_list = [keyword for keyword, match in keywords]

        # Get the page title
        page_title = self.driver.title

        return {"title":page_title, "main_content":main_content, "keywords":keywords_list}

    def find_sitemap(self, website_base_url:str) -> str|None:
        if website_base_url[-1] == "/":
            website_base_url = website_base_url[:-1]

        #Get sitemap
        sitemap_location = ""
        sitemap_found = False

        #In robots.txt
        self.driver.get(website_base_url+"/robots.txt")
        try:
            robots_text = self.driver.find_element(By.CSS_SELECTOR, "body").text
            sitemap_match = re.search(self.sitemap_in_robots_regex_pattern, robots_text)
    
            if sitemap_match:
                sitemap_location = sitemap_match.group("sitemap_url")
                sitemap_found = True
        except Exception as e:
            pass

        #On one of the paths
        for sitemap_possible_location in self.sitemap_locations:
            if sitemap_found:
                break

            possible_sitemap_url = website_base_url + sitemap_possible_location

            response = requests.get(possible_sitemap_url)
            if response.status_code == 200:
                sitemap_location = possible_sitemap_url
                sitemap_found = True

        return sitemap_location if sitemap_location != "" else None

    def crawl_website(self, website_base_url:str):
        #Get the sitemap
        sitemap_url = self.find_sitemap(website_base_url)
        print(sitemap_url)

        # Extract page domain
        domain_match = re.match(self.url_regex_pattern, website_base_url)
        page_domain = str(domain_match.group("domain_name")) + str(domain_match.group("top_level_domain"))

    def run(self):
        while True:
            website_to_crawl_url = self.get_next_website_to_crawl()

            if website_to_crawl_url == None:
                time.sleep(1)
                continue

            self.crawl_website(website_to_crawl_url)

MangoCrawler().run()