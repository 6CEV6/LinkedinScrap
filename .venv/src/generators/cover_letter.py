# src/cover_letter.py
import os
import openai
import logging

logger = logging.getLogger(__name__)

class CoverLetterGenerator:
    def __init__(self, openai_api_key: str):
        openai.api_key = openai_api_key

    def process_job(self, job_listing):
        try:
            # Generate a cover letter for the job listing
            prompt = f"Write a cover letter for the following job posting:\n\nTitle: {job_listing.title}\nCompany: {job_listing.company}\nLocation: {job_listing.location}\nDescription: {job_listing.description}"
            response = openai.Completion.create(
                engine="text-davinci-002",
                prompt=prompt,
                max_tokens=1024,
                n=1,
                stop=None,
                temperature=0.7,
            )

            cover_letter = response.choices[0].text.strip()
            logger.info(f"Generated cover letter for job: {job_listing.title}")
            return cover_letter
        except Exception as e:
            logger.error(f"Error generating cover letter: {e}")
            return None