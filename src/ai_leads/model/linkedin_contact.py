import logging
from ai_leads.model.navigator import WebpageScraper
from ai_leads.model.lead_dataset_creation import LeadDataFrameConverter

from typing import List

# Setup logging
logger = logging.getLogger(__name__)


class LinkedInContactRetriever:
    """A utility class to find linkedIn contact relevant"""

    def __init__(self):
        self.scraper = WebpageScraper()
        self.converter = LeadDataFrameConverter()

    @staticmethod
    def format_query(company: str) -> str:
        """
        Generates a query able to find relevant linkedin profiles for a company

        Args:
            company (str): name of the company

        Returns:
            str: correct query format
        """
        query = f'"{company}" responsable ressources humaines profile site:fr.linkedin.com/in/'
        return query

    @staticmethod
    def check_if_profile(url: str) -> bool:
        """
        Check if a url is a linkedin profile

        Args:
            url (str): url

        Returns:
            bool: True if profile, False if not
        """
        if ("/in/" in url) and ("linkedin" in url):
            return True
        return False

    def find_relevant_profiles(self, company: str) -> List[str]:
        """
        Generate a list of url that are potentially relevant linkedin profiles for a company

        Args:
            company (str): name of the company

        Returns:
            List: list of relavtn urls
        """
        scraper = self.scraper
        query = self.format_query(company)
        url_list = scraper.get_raw_google_links(query)
        url_list = [url for url in url_list if self.check_if_profile(url)]
        return url_list
