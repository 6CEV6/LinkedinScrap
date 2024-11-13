from datetime import datetime
from typing import Dict, Optional

class JobListing:
    def __init__(self, title: str, company: str, location: str, description: str,
                 salary: Optional[str], url: str, source: str):
        self.title = title
        self.company = company
        self.location = location
        self.description = description
        self.salary = salary
        self.url = url
        self.source = source
        self.date_found = datetime.now().strftime("%Y-%m-%d")

    def to_dict(self) -> Dict:
        return {
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'description': self.description,
            'salary': self.salary,
            'url': self.url,
            'source': self.source,
            'date_found': self.date_found
        }
