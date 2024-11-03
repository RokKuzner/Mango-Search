from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import selenium.common.exceptions

from fake_useragent import UserAgent
from urllib.parse import urlparse, urlunparse

from bs4 import BeautifulSoup
from keybert import KeyBERT

import re
import requests

class MangoCrawler():
    def __init__(self) -> None:
        # Global variables
        self.url_regex_pattern = re.compile(r"^(?:https?:\/\/)(?:www\.)?(?P<domain_name>[a-zA-Z0-9](?:[a-zA-Z0-9\-\.]{0,251}[a-zA-Z0-9])?)(?P<top_level_domain>\.[a-zA-Z]{2,63})(?::(?P<port>\d{1,5}))?(?P<subpages>\/[^\?#]*)?(?P<arguments>\?[^#]*)?(?P<fragment>#.*)?$")
        self.sitemap_in_robots_regex_pattern = re.compile(r"(?:sitemap)(?::)(?: )(?P<sitemap_url>(?:https?:\/\/)(?:www\.)?(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-\.]{1,251}[a-zA-Z0-9])?)(?:\.[a-zA-Z0-9\-]{2,63})(?:(?:\:)(\d{4}))?(?:\/.*))", flags=re.M|re.I)
        self.sitemap_locations = ["/sitemap.xml",  "/sitemap-index.xml", "/sitemap/sitemap.xml", "/sitemapindex.xml", "/sitemap/index.xml", "/sitemap1.xml"]
        self.db_interface_url = 'http://db-interface:5000'

        #Initialize the state of the crawler
        self.is_active = False

        # Set up the options for chrome webdriver
        self.user_agent = UserAgent()
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"user-agent={self.user_agent.random}")

        # Create the driver
        self.driver = webdriver.Chrome(options=chrome_options)
    
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
        self.request_counter += 1  # Increment counter

        # Get the page source and parse it with BeautifulSoup
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Remove non-content sections
        self.filter_out_non_content(soup)

        # Extract main content
        main_content = self.extract_main_content(soup)

        #Extract content keywords
        content_keywords_amount = min(max(len(main_content)//20, 2), 20)
        kw_model = KeyBERT()
        content_keywords = kw_model.extract_keywords(main_content, keyphrase_ngram_range=(1, 2), stop_words=None, top_n=content_keywords_amount)
        content_keywords_list = [keyword for keyword, match in content_keywords]

        #Extract keywords form meta
        try:
            meta_tag = self.driver.find_element(By.CSS_SELECTOR, 'meta[name="keywords"]')
            meta_keywords = meta_tag.get_attribute("content")
            meta_keywords = [keyword for keyword in re.split(r"\s*\,\s*", meta_keywords) if keyword] #Extract all words form the meta tag that are separated by (","+any amount of spaces) and strip the list of any empty strings
        except selenium.common.exceptions.NoSuchElementException:
            meta_keywords = []

        # Get the page title
        page_title = self.driver.title

        return {"title":page_title, "main_content":main_content, "content_keywords":content_keywords_list, "meta_keywords":meta_keywords}

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
    
    def find_subpages(self, website_base_url:str) -> list[str]:
        to_explore = [website_base_url]
        explored = set()

        subpages = []

        while to_explore:
            print(f"Page n: {len(subpages)}")

            webpage_url = to_explore.pop(0)
            if webpage_url in explored:
                continue

            try:
                self.driver.get(webpage_url)
                subpages.append(webpage_url)
                explored.add(webpage_url)
            except:
                explored.add(webpage_url)
                continue

            #Get all links in this webpage
            anchor_elements = self.driver.find_elements(By.CSS_SELECTOR, "a")
            for anchor_element in anchor_elements:
                try:
                    link = anchor_element.get_attribute("href")
                except:
                    continue
                if not link or not link.startswith(website_base_url):continue

                #Clean the link
                parsed_link = urlparse(link)
                link = urlunparse((parsed_link.scheme, parsed_link.netloc, parsed_link.path, "", "", ""))
                if not link.endswith("/"): link += "/"

                #Add the link to subpages
                if link not in explored:
                    to_explore.append(link)

        return subpages

    def crawl_website(self, website_base_url:str):
        #Set the state to active
        self.is_active = True

        # Extract page domain
        url_match = re.match(self.url_regex_pattern, website_base_url)
        website_domain_name = url_match.group("domain_name")

        #Extract keypharse from the domain name
        domain_name_parts = [part for part in re.split(r"[\.\-]", website_domain_name) if part] #Extract all words form the domain name that are separated by "." or "-" and strip the list of any empty strings
        domain_name_keyphrase = " ".join(domain_name_parts)

        #Crawl the index page
        index_webpage_data = self.crawl_webpage(website_base_url)

        keywords = [ domain_name_keyphrase, index_webpage_data["title"] ] + index_webpage_data["content_keywords"] + index_webpage_data["meta_keywords"]
        keywords = [keyword.lower() for keyword in keywords] #Lowercase all the keywords

        #Remove all duplicate and empty keywords
        non_duplicate_keywords = set()
        for keyword in keywords:
            if keyword and keyword not in non_duplicate_keywords:
                non_duplicate_keywords.add(keyword)

        keywords = [keyword for keyword in non_duplicate_keywords]

        #TODO: Add keywords to the database

        self.driver.quit()
        self.is_active = False