# src/job_filter.py
class JobFilter:
    def __init__(self, config: dict):
        self.config = config

    def filter_jobs(self, jobs: list):
        # Implement your job filtering logic here
        return [job for job in jobs if job.company != 'Acme Corp']