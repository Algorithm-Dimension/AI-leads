from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote
import logging
import time
from Config.param import INDEED_NUMBER_PAGE, LINKEDIN_NUMBER_SCROLL

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebScraper:
    """
    A class to handle web scraping using Selenium.

    Attributes:
        url (str): The URL to be scraped.
        driver (webdriver): The Selenium webdriver instance.
        source (str): The name of the source website, e.g., 'LinkedIn', 'Indeed'.
    """

    def __init__(self, source, job, location, options=None):
        """
        Initializes the WebScraper with a URL.

        Args:
            url (str): The URL to be scraped.
            options (webdriver.ChromeOptions, optional): Custom Chrome options. Defaults to None.
        """
        self.driver = self._init_driver(options)
        self.source = source
        self.job = job
        self.location = location
        self.indeed_number_page = INDEED_NUMBER_PAGE
        self.linkedin_number_scroll = LINKEDIN_NUMBER_SCROLL

    def _init_driver(self, options=None) -> webdriver:
        """Initializes the Selenium webdriver with given options."""
        if options is None:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
        return webdriver.Chrome(options=options)

    def next_page_indeed(self, wait_time=5) -> bool:
        """Navigates to the next page on an Indeed website."""
        try:
            WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'a[data-testid="pagination-page-next"]'))
            )
            next_page_button = self.driver.find_element(By.CSS_SELECTOR, 'a[data-testid="pagination-page-next"]')
            self.driver.execute_script("arguments[0].scrollIntoView();", next_page_button)
            next_page_button.click()
            logger.info("Successfully navigated to the next page on Indeed.")
            time.sleep(wait_time)
            return True
        except Exception as e:
            logger.debug(f"Error navigating to the next page: {str(e)}")
            return False

    def scroll(self, num_scrolls=3, scroll_pause_time=2):
        """Scrolls down the webpage a specified number of times."""
        for _ in range(num_scrolls):
            try:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                logger.info(f"Successfully scrolled ({_ + 1} times)")
                time.sleep(scroll_pause_time)
            except Exception as err:
                logger.debug("Error while scrolling.")
                return

    def get_webpage_source(self, url, wait_time=5, scroll_pause_time=2) -> str:
        """Fetches the webpage's HTML source after performing necessary interactions."""
        html_content = ""
        try:
            self.driver.get(url)
            time.sleep(wait_time)

            if self.source == "LinkedIn":
                num_scrolls = self.linkedin_number_scroll
                self.scroll(num_scrolls, scroll_pause_time)
                html_content = self.driver.page_source
            elif self.source == "Indeed":
                num_pages = self.indeed_number_page
                html_content = self.driver.page_source
                for _ in range(num_pages):
                    if not self.next_page_indeed(wait_time):
                        break
                    html_content += self.driver.page_source

        except Exception as e:
            logger.debug(f"Error getting the webpage source: {str(e)}")

        self.driver.quit()
        return html_content

    def find_url(self):
        source, job, location = self.source, self.job, self.location
        if source == "Indeed":
            url = f"https://fr.indeed.com/q-{job}-l-{location}-emplois.html"
        elif source == "LinkedIn":
            url = self._extract_first_links_from_google()
        return(url)

    def _extract_first_links_from_google(self):
        driver, source, job, location = self.driver, self.source, self.job, self.location
        query = f"{job} {location} {source} jobs"
        links = [] # Initiate empty list to capture final results
        # Specify number of pages on google search, each page contains 10 #links
        n_pages = 2
        for page in range(1, n_pages):
            query_encoded = quote(query)
            # Construisez l'URL avec la requête encodée
            url = "http://www.google.com/search?q=" + query_encoded + "&start=" + str((page - 1) * 10)
            try:
                driver.get(url)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                search = soup.find_all('div', class_="yuRUbf")
                for h in search:
                    url = h.a.get('href')
                    links.append(url)
            except Exception as err:
                print(err)
        return(links[1])


    def extract_readable_text_from_html(html: str) -> str:
        """
        Extracts readable text from the provided HTML using BeautifulSoup.

        Args:
            html (str): The HTML string.

        Returns:
            str: Extracted readable text.
        """
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        return ' '.join(text.split())

    def extract_readable_text(self) -> str:
        """
        Scrapes and extracts readable text from a given URL.

        Args:
            url (str): The URL to be scraped.

        Returns:
            str: Extracted readable text.
        """
        url = self.find_url()
        html_source = self.get_webpage_source(url)
        if html_source:
            return self.extract_readable_text_from_html(html_source)
        logger.debug(f"Failed to fetch content from the URL: {url}")
        return ""
