# src/scrapers/justjoin_scraper.py
import sys
sys.path.append("src")
import json
import logging
from typing import List, Dict
from dataclasses import dataclass
import requests

logger = logging.getLogger(__name__)

@dataclass
class JobListing:
    title: str
    company: str
    location: str
    description: str
    salary: str
    url: str
    source: str

class JustJoinScraper:
    def __init__(self, headers: Dict):
        self.headers = headers
        self.base_url = "https://justjoin.it/"
        self.session = requests.Session()
        self.session.headers.update(headers)

    def scrape_jobs(self, search_query: str, location: str) -> List[JobListing]:
        """
        Scrape jobs from JustJoin.it API
        """
        try:
            logger.info(f"Fetching jobs from JustJoin.it for query: {search_query}, location: {location}")

            # JustJoin.it provides a public API endpoint that returns all offers
            response = self.session.get(self.base_url)
            response.raise_for_status()

            jobs_data = response.json()
            listings = []

            for job in jobs_data:
                # Filter jobs based on search criteria
                if (search_query.lower() in job.get('title', 'Data Engineer').lower() or
                        search_query.lower() in job.get('body', '').lower()):
                    if not location or location.lower() in job.get('city', '').lower():
                        try:
                            salary_range = self._format_salary(job.get('salary'))
                            listing = JobListing(
                                title=job.get('title', 'Data Engineer'),
                                company=job.get('company_name', ''),
                                location=f"{job.get('city', 'Poland')}, {job.get('country_code', 'PL')}",
                                description=job.get('body', ''),
                                salary=salary_range,
                                url=f"https://justjoin.it/{job.get('id')}",
                                source='JustJoin.it'
                            )
                            listings.append(listing)
                        except Exception as e:
                            logger.error(f"Error processing job listing: {e}")
                            continue

            logger.info(f"Found {len(listings)} matching jobs on JustJoin.it")
            return listings

        except Exception as e:
            logger.error(f"Error scraping JustJoin.it: {e}")
            return []

    @staticmethod
    def _format_salary(salary_data: Dict) -> str:
        """Format salary information from JustJoin.it format"""
        if not salary_data:
            return "Not specified"

        try:
            from_salary = salary_data.get('from')
            to_salary = salary_data.get('to')
            currency = salary_data.get('currency')

            if from_salary and to_salary:
                return f"{from_salary}-{to_salary} {currency}"
            elif from_salary:
                return f"From {from_salary} {currency}"
            elif to_salary:
                return f"Up to {to_salary} {currency}"
            else:
                return "Not specified"
        except Exception:
            return "Not specified"