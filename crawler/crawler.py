# File: crawler.py
# This file crawls given URL pages, discovers chatbot API endpoints, classifies domains, and registers bots in the Neo4j database.

# Imports needed packages
import logging
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

from crawler.classifier import classify_bot
from db.neo4j_driver import Neo4jDriver

logger = logging.getLogger(__name__)

# Class to crawl webpages and upload data to neo4j db
class ChatbotCrawler:
    def __init__(self, urls: list[str]):
        self.urls = urls
        self.driver = Neo4jDriver()

    # detects if a webpage has a chatbot
    def detect_chatbot(self, html: str) -> bool:
        soup = BeautifulSoup(html, "html.parser")
        if soup.find("textarea"):
            return True
        if soup.find(attrs={
            "class": re.compile(r"chat", re.I),
            "id": re.compile(r"chat", re.I)
        }):
            return True
        for script in soup.find_all("script", src=True):
            if re.search(r"chat", script["src"], re.I):
                return True
        return False

    # If a page has a chatbot it discovers the chatbot url
    def extract_api_url(self, html: str, base_url: str) -> str:
        soup = BeautifulSoup(html, "html.parser")

        for script in soup.find_all("script"):
            if script.string:
                match = re.search(r"fetch\(['\"](/[^'\"]*chat)[\"']", script.string)
                if match:
                    return urljoin(base_url, match.group(1))

        parsed = urlparse(base_url)
        return f"{parsed.scheme}://{parsed.netloc}/chat"

    # Generate the bot id
    def generate_bot_id(self, api_url: str) -> str:
        parsed = urlparse(api_url)
        return parsed.netloc

    # generate the bot name
    def generate_bot_name(self, api_url: str) -> str:
        parsed = urlparse(api_url)
        name = parsed.netloc.split('.')[0]
        return name.capitalize()

    # Main method to search webpages and register any bots
    def discover_and_register(self) -> list:
        found = []

        for url in self.urls:
            try:
                resp = requests.get(url, timeout=5)
                resp.raise_for_status()
                html = resp.text

                if not self.detect_chatbot(html):
                    logger.info(f"No chatbot UI found at {url}")
                    continue

                # Extract API endpoint from HTML
                api_url = self.extract_api_url(html, url)

                # Classify domain based on page content and original URL
                domain = classify_bot(html, url)

                # Generate identifiers
                bot_id = self.generate_bot_id(api_url)
                bot_name = self.generate_bot_name(api_url)

                # Register in Neo4j
                self.driver.insert_bot(bot_id, bot_name, domain, api_url)
                logger.info(
                    f"Registered bot '{bot_name}' (id={bot_id}) domain='{domain}' api_url='{api_url}'"
                )

                # Append to found list
                found.append({"bot_id": bot_id, "bot_name": bot_name, "domain": domain, "api_url": api_url})

            except Exception as e:
                logger.error(f"Error crawling {url}: {e}")

        self.driver.close()
        return found

