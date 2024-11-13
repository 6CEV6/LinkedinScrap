from typing import Dict, Optional, List
import requests
from bs4 import BeautifulSoup
from models.job_listing import JobListing


class BaseScraper:
    def __init__(self, headers: Dict):
        self.headers = headers
        self.session = requests.Session()

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        try:
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def scrape_jobs(self, search_query: str, location: str) -> List[JobListing]:
        """
        Abstract method to be implemented by specific scrapers
        """
        raise NotImplementedError("Subclasses must implement scrape_jobs method")