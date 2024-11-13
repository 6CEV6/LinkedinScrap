# src/scrapers/linkedin_scraper.py
import sys
sys.path.append("src")
import time
import logging
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dataclasses import dataclass

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

class LinkedInScraper:
    def __init__(self, headers: Dict, linkedin_username: str = None, linkedin_password: str = None):
        self.headers = headers
        self.linkedin_username = linkedin_username
        self.linkedin_password = linkedin_password
        self.driver = None

    def _setup_driver(self):
        """Setup Selenium WebDriver with Chrome"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        # Add headers to requests
        for key, value in self.headers.items():
            options.add_argument(f'--header={key}:{value}')

        self.driver = webdriver.Chrome(options=options)

    def _login_to_linkedin(self):
        """Login to LinkedIn if credentials are provided"""
        if not self.linkedin_username or not self.linkedin_password:
            logger.warning("LinkedIn credentials not provided. Some jobs might not be visible.")
            return

        try:
            self.driver.get("https://www.linkedin.com/login")

            # Wait for login form and enter credentials
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            password_field = self.driver.find_element(By.ID, "password")

            username_field.send_keys(self.linkedin_username)
            password_field.send_keys(self.linkedin_password)
            password_field.send_keys(Keys.RETURN)

            # Wait for login to complete
            time.sleep(3)
            logger.info("Successfully logged in to LinkedIn")

        except Exception as e:
            logger.error(f"Failed to login to LinkedIn: {e}")

    def scrape_jobs(self, search_query: str, location: str) -> List[JobListing]:
        """
        Scrape jobs from LinkedIn using Selenium
        """
        try:
            if not self.driver:
                self._setup_driver()
                self._login_to_linkedin()

            # Construct search URL
            search_url = (
                f"https://www.linkedin.com/jobs/search/?"
                f"keywords={search_query}&location={location}"
                f"&f_TPR=r86400&sortBy=DD"  # Last 24 hours, sorted by date
            )

            logger.info(f"Fetching jobs from LinkedIn: {search_url}")
            self.driver.get(search_url)

            # Wait for job listings to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobs-search__results-list"))
            )

            # Scroll to load more jobs
            self._scroll_to_load_jobs()

            # Extract job listings
            job_cards = self.driver.find_elements(By.CLASS_NAME, "jobs-search-results__list-item")
            listings = []

            for card in job_cards:
                try:
                    # Click on job card to load details
                    card.click()
                    time.sleep(1)  # Wait for job details to load

                    # Extract job information
                    title = card.find_element(By.CLASS_NAME, "job-card-list__title").text
                    company = card.find_element(By.CLASS_NAME, "job-card-container__company-name").text
                    location = card.find_element(By.CLASS_NAME, "job-card-container__metadata-item").text

                    # Wait for job description to load in side panel
                    description = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "jobs-description"))
                    ).text

                    # Get job URL
                    url = card.find_element(By.CLASS_NAME, "job-card-list__title").get_attribute("href")

                    # Try to get salary information
                    try:
                        salary = card.find_element(By.CLASS_NAME, "job-card-container__salary-info").text
                    except NoSuchElementException:
                        salary = "Not specified"

                    listing = JobListing(
                        title=title,
                        company=company,
                        location=location,
                        description=description,
                        salary=salary,
                        url=url,
                        source='LinkedIn'
                    )
                    listings.append(listing)

                except Exception as e:
                    logger.error(f"Error processing LinkedIn job card: {e}")
                    continue

            logger.info(f"Found {len(listings)} matching jobs on LinkedIn")
            return listings

        except Exception as e:
            logger.error(f"Error scraping LinkedIn: {e}")
            return []

        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None

    def _scroll_to_load_jobs(self):
        """Scroll through the page to load more job listings"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for new content to load

            # Calculate new scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")

            # Break if no more content is loading
            if new_height == last_height:
                break

            last_height = new_height