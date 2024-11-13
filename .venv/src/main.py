import sys
sys.path.append("src")
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
import yaml
from scraper.linkedin_scraper import LinkedInScraper
from scraper.justjoin_scraper import JustJoinScraper
from job_filter import JobFilter

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('job_scraper.log'),
            logging.StreamHandler()
        ]
    )

def load_environment():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)

def load_config():
    """Load configuration from config.yaml"""
    config_path = Path(__file__).parent.parent / 'config' / 'config.yaml'
    with open(config_path) as f:
        return yaml.safe_load(f)

def main():
    # Setup
    setup_logging()
    logger = logging.getLogger(__name__)
    load_environment()
    config = load_config()

    # Initialize scrapers
    scraper = [
        LinkedInScraper(
            headers=config['scraping']['headers'],
            linkedin_username=os.getenv('LINKEDIN_USERNAME'),
            linkedin_password=os.getenv('LINKEDIN_PASSWORD')
        ),
        JustJoinScraper(headers=config['scraping']['headers'])
    ]

    # Initialize other components
    job_filter = JobFilter(config['filters'])

    all_jobs = []

    # Run job search on all platforms
    for scraper in scraper:
        logger.info(f"Starting job search with {scraper.__class__.__name__}")
        jobs = scraper.scrape_jobs(
            config['search']['query'],
            config['search']['location']
        )
        all_jobs.extend(jobs)

    # Filter jobs
    filtered_jobs = job_filter.filter_jobs(all_jobs)
    logger.info(f"Found {len(filtered_jobs)} matching jobs after filtering")

    # Process jobs
    for job in filtered_jobs:
        cover_letter_generator.process_job(job)

if __name__ == "__main__":
    main()