from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebScraper:
    def __init__(self, url: str, options=None):
        self.url = url
        self.driver = self._init_driver(options)
        self.source = self._identify_source()

    def _init_driver(self, options=None) -> webdriver:
        if options is None:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
        return webdriver.Chrome(options=options)

    def _identify_source(self) -> str:
        if "linkedin" in self.url:
            return "LinkedIn"
        elif "indeed" in self.url:
            return "Indeed"
        return ""

    def next_page_indeed(self, wait_time=5) -> bool:
        try:
            # Waiting for the next button to load
            WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'a[data-testid="pagination-page-next"]'))
            )
            # Finding and clicking the button
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
        for _ in range(num_scrolls):
            try:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                logger.info(f"Successfully scrolled ({_ + 1} times)")
                time.sleep(scroll_pause_time)
            except Exception as err:
                logger.debug("Error while scrolling.")
                return

    def get_webpage_source(self, wait_time=5, num_scrolls=30, scroll_pause_time=2) -> str:
        html_content = ""
        try:
            self.driver.get(self.url)
            time.sleep(wait_time)

            if self.source == "LinkedIn":
                self.scroll(num_scrolls, scroll_pause_time)
                html_content = self.driver.page_source
            elif self.source == "Indeed":
                html_content = self.driver.page_source
                for _ in range(2):
                    if not self.next_page_indeed(wait_time):
                        break
                    html_content += self.driver.page_source

        except Exception as e:
            logger.debug(f"Error getting the webpage source: {str(e)}")

        self.driver.quit()
        return html_content


def extract_readable_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    return ' '.join(text.split())


def extract_readable_text(url: str) -> str:
    scraper = WebScraper(url)
    html_source = scraper.get_webpage_source()
    if html_source:
        return extract_readable_text_from_html(html_source)
    logger.debug(f"Failed to fetch content from the URL: {url}")
    return ""
