import logging
import re
from typing import List
import urllib.parse

from ai_leads.model.lead_dataset_creation import LeadDataFrameConverter
from ai_leads.model.llm_model import LLMManager
from ai_leads.model.navigator import WebpageScraper

# Setup logging
logger = logging.getLogger(__name__)


class LinkedInContactRetriever:
    """A utility class to find linkedIn contact relevant"""

    def __init__(self):
        self.scraper = WebpageScraper()
        self.llm_manager = LLMManager()
        self.lead_converter = LeadDataFrameConverter()

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
            List: list of relevant urls
        """
        scraper = self.scraper
        query = self.format_query(company)
        url_list = scraper.get_raw_google_links(query)
        url_list = [url for url in url_list if self.check_if_profile(url)]
        # url_list = url_list + [np.nan] * (2 - len(url_list))
        return url_list

    @staticmethod
    def find_name_from_linkedin_url(url: str) -> List[str]:
        """
        Find first name and last name from linkedin profile
        Args:
            url (str): linkedin profile url

        Returns:
            fisrt_name: str
            last_name: str
        """
        try:
            # Decode the URL to handle special characters
            decoded_url = urllib.parse.unquote(url)

            # Extract the first and last name using regular expressions
            match = re.search(r"/in/([^/]+)-([^/]+)-\w+", decoded_url)

            if match:
                first_name = match.group(1)
                last_name = match.group(2)
            else:
                first_name = ""
                last_name = ""
            return [first_name.title(), last_name.title()]
        except Exception:
            return ["", ""]
