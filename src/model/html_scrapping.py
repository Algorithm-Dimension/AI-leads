from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time
from urllib.parse import quote
from typing import List
from Config.param import INDEED_NUMBER_PAGE, LINKEDIN_NUMBER_SCROLL

# Setting up logging
logger = logging.getLogger(__name__)


class WebScraper:
    """
    A class to scrape web content from LinkedIn and Indeed using Selenium and BeautifulSoup.

    Attributes:
        url (str): URL of the webpage to be scraped.
        driver (webdriver): Selenium web driver instance.
        source (str): Source website identifier, either "LinkedIn" or "Indeed".

    Methods:
        next_page_indeed(): Navigate to the next page on Indeed.
        scroll(): Scroll the web page multiple times.
        get_webpage_source(): Get the HTML content of the web page.
    """

    def __init__(self, platform="Google", options=None):
        """
        Initialize a new WebScraper instance.

        Args:
            plateforme (str): platform to be scraped.
            options: Selenium webdriver options, default to None.
        """
        self.driver = self._init_driver(options)
        self.platform = platform
        self.indeed_number_page = INDEED_NUMBER_PAGE
        self.linkedin_number_scroll = LINKEDIN_NUMBER_SCROLL

    def _init_driver(self, options=None) -> webdriver.Chrome:
        """
        Initialize a Selenium web driver with specified options or defaults.

        Args:
            options: Selenium webdriver options, default to None.

        Returns:
            webdriver.Chrome: Initialized Chrome web driver.
        """
        if options is None:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
        return webdriver.Chrome()

    @staticmethod
    def _identify_source(url) -> str:
        """
        Identify the source website based on the provided URL.

        Returns:
            str: "LinkedIn", "Indeed", or an empty string if unrecognized.
        """
        if "linkedin" in url:
            return "LinkedIn"
        elif "indeed" in url:
            return "Indeed"
        return ""

    def next_page_indeed(self, wait_time=5) -> bool:
        """
        Navigate to the next page on Indeed if available.

        Args:
            wait_time (int): Time in seconds to wait for elements to load.

        Returns:
            bool: True if successfully navigated, otherwise False.
        """
        try:
            WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'a[data-testid="pagination-page-next"]')
                )
            )
            next_page_button = self.driver.find_element(
                By.CSS_SELECTOR, 'a[data-testid="pagination-page-next"]'
            )
            self.driver.execute_script(
                "arguments[0].scrollIntoView();", next_page_button
            )
            next_page_button.click()
            print("Successfully navigated to the next page on Indeed.")
            time.sleep(wait_time)
            return True
        except Exception as error:
            print(f"Error navigating to the next page: {str(error)}")
            return False

    def scroll(self, num_scrolls=LINKEDIN_NUMBER_SCROLL, scroll_pause_time=2):
        """
        Scroll the web page multiple times.

        Args:
            num_scrolls (int): Number of times to scroll the page.
            scroll_pause_time (int): Time in seconds to pause between scrolls.
        """
        for _ in range(num_scrolls):
            try:
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
                logger.info(f"Successfully scrolled ({_ + 1} times)")
                time.sleep(scroll_pause_time)
            except Exception as err:
                logger.debug("Error while scrolling.")
                return

    def get_webpage_source(
        self, url, wait_time=5, num_scrolls=LINKEDIN_NUMBER_SCROLL, scroll_pause_time=2
    ) -> str:
        """
        Get the HTML content of the web page.

        Args:
            wait_time (int): Time in seconds to wait for the webpage to load.
            num_scrolls (int): Number of times to scroll the page.
            scroll_pause_time (int): Time in seconds to pause between scrolls.

        Returns:
            str: HTML content of the web page.
        """
        html_content = ""
        try:
            self.driver.get(url)
            time.sleep(wait_time)

            if self.platform == "LinkedIn":
                self.scroll(num_scrolls, scroll_pause_time)
                html_content = self.driver.page_source
            elif self.platform == "Indeed":
                html_content = self.driver.page_source
                for _ in range(INDEED_NUMBER_PAGE):
                    print("INDEEEEED", _)
                    self.next_page_indeed(wait_time)
                    html_content += self.driver.page_source

        except Exception as e:
            logger.debug(f"Error getting the webpage source: {str(e)}")

        self.driver.quit()
        return html_content

    @staticmethod
    def extract_readable_text_from_html(html: str) -> str:
        """
        Extract readable text from an HTML content using BeautifulSoup.

        Args:
            html (str): HTML content.

        Returns:
            str: Extracted readable text.
        """
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text()
        return " ".join(text.split())

    def extract_readable_text(self, url: str) -> str:
        """
        Extract readable text from a web page URL.

        Args:
            url (str): Web page URL.

        Returns:
            str: Extracted readable text, or an empty string if failed.
        """
        html_source = self.get_webpage_source(url)
        if html_source:
            return self.extract_readable_text_from_html(html_source)
        logger.debug(f"Failed to fetch content from the URL: {url}")
        return ""

    def _extract_google_links(
        self, position: str, location: str, num_results: int = 5
    ) -> List[str]:
        """
        Extract the first set of links from a Google search.

        Args:
        - position: job position
        - location: location of the job
        - num_results: Number of results to fetch.

        Returns:
        - list: List of URLs from the Google search.
        """
        platform = self.platform
        query = f"{position} {location} {platform}"
        links = []
        n_pages = 2
        print("QUERY = ", query)
        for page in range(1, n_pages):
            query_encoded = quote(query)
            url = f"http://www.google.com/search?q={query_encoded}&start={(page - 1) * 10}"
            print("URL GOOOG", url)
            try:
                self.driver.get(url)
                time.sleep(5)
                self.scroll(1, 2)
                html_content = self.driver.page_source
                soup = BeautifulSoup(html_content, "html.parser")
                search_results = soup.find_all("div", class_="yuRUbf")

                for result in search_results:
                    link = result.a.get("href")
                    links.append(link)

            except Exception as err:
                print(err)
        print("LINK : ", links)
        return links[:num_results]

    def _linkedin_url(self, position: str, location: str) -> List[str]:
        """
        Function which returns the linkedin web page with job offers
        Args:
        - position: job position
        - location: location of the job

        Returns:
        - str: URL with job offer
        """
        return f"https://www.linkedin.com/jobs/{position}-jobs-{location}/"

    def _indeed_url(self, position: str, location: str) -> List[str]:
        """
        Function which returns the indeed web page with job offers
        Args:
        - position: job position
        - location: location of the job

        Returns:
        - str: URL with job offer
        """
        return f"https://fr.indeed.com/q-{position}-l-{location}-emplois.html"

    def find_url(self, position: str, location: str) -> str:
        """
        Function which return according to the plateform, the position and the location the url to scrap
        Args:
        - position: job position
        - location: location of the job

        Output: url: str"""

        if self.platform == "LinkedIn":
            url = self._linkedin_url(position, location)
            return url
        if self.platform == "Indeed":
            url = self._indeed_url(position, location)
            return url
