import logging
import random
import time
from typing import List
from urllib.parse import quote

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium_recaptcha_solver import RecaptchaSolver

from ai_leads.Config.param import N_PROBA, SPORT_WEBSITE_LIST, WAIT_TIME

# from selenium_recaptcha import Recaptcha_Solver


# Setup logging
logger = logging.getLogger(__name__)


class WebpageScraper:
    """A utility class to scrape web pages using Selenium and
    parse content with BeautifulSoup."""

    def __init__(self, platform: str = "", headless: bool = False):
        self.options = webdriver.ChromeOptions()
        if headless:
            self.options.add_argument("--headless")
        self.logger = logger
        self.platform = platform
        self.dynamic = self.__init__dynamic(platform)
        self.driver = None
        self.random_action()

    @staticmethod
    def random_waiting_time(waiting_time: int = WAIT_TIME):
        """Pause l'exécution pour un temps aléatoire entre 1 et 5 secondes."""
        wait_time = random.randint(1, waiting_time)  # noqa: Génère un temps d'attente aléatoire entre 1 et 5
        time.sleep(wait_time)  # Pause l'exécution pour le temps généré

    def random_action(self):
        """Va sur un site au hasard"""
        driver = self.driver
        try:
            url = random.choice(SPORT_WEBSITE_LIST)
            driver.get(url)
            self.random_waiting_time()
        except Exception:
            return

    def random_stochastic_action(self, n_proba: int = N_PROBA):
        """Vas sur un site au hasard avec la probabilité 1/n_proba lorsque
        que la fonction fetch_html est appelée"""
        random_number = random.randint(1, n_proba)
        if random_number == 1:
            self.random_action()

    @staticmethod
    def __init__dynamic(platform: str) -> bool:
        """
        Get the type of scrapping. True if we need to scroll. Else, False

        Args:
        - platform: The platform job board where we want to retrieve the jobs

        Returns:
        - bool: True/False
        """
        if platform in ["LinkedIn"]:
            return True
        elif platform in ["Indeed", "Hello Work", "Cadre Emploi", "Welcome to the Jungle", "Talent.com"]:
            return False
        return False

    def close_driver(self):
        """Ferme le WebDriver explicitement."""
        self.driver.quit()

    def fetch_html(self, url: str) -> str:
        """
        Get the HTML source of a webpage using Selenium.

        Args:
        - url: The URL of the webpage to fetch.

        Returns:
        - str: HTML source of the webpage.
        """
        if self.driver is None:
            self.driver = webdriver.Chrome(options=self.options)  # Initialisation du WebDriver ici
        driver = self.driver
        try:
            self.random_stochastic_action()
            driver.get(url)
            driver.implicitly_wait(WAIT_TIME)
            if self.dynamic:
                self.scroll(driver, num_scrolls=10, scroll_pause_time=2)
            html_content = driver.page_source
            if self.check_if_blocked_by_captcha(html_content):
                try:
                    self.solve_recaptcha_v2(driver)
                    self.random_waiting_time()
                    logger.info("Captcha successfully solved")
                except Exception:
                    pass
                html_content = driver.page_source
            return html_content
        except Exception as error:
            logger.info("An error occured: %s", error)
        return html_content

    @staticmethod
    def extract_readable_text_from_html(html: str) -> str:
        """
        Extract readable text from an HTML string using BeautifulSoup.

        Args:
        - html: The HTML string.

        Returns:
        - str: The extracted readable text.
        """
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text()
        return " ".join(text.split())

    def fetch_readable_text(self, url: str) -> str:
        """
        Fetch readable text from a given URL.

        Args:
        - url: The URL of the webpage.

        Returns:
        - str: The extracted readable text from the URL's content.
        """
        try:
            html_source = self.fetch_html(url)
            text = self.extract_readable_text_from_html(html_source)
            if self.is_correctly_scraped(text):
                return text
            else:
                time.sleep(30)
                html_source = self.fetch_html(url)
                text = self.extract_readable_text_from_html(html_source)
                return text
        except Exception as error:
            print("An error occurred:", str(error))
            return None

    @staticmethod
    def is_correctly_scraped(text: str, threshold=100) -> bool:
        """
        Function that detects is the web page has correcrlty been scraped
        Logic: We consider the page is not scrapped if the text is very short, so lets fix a
        length threshold under we consider an error
        Args:
        - text: str
        - threshold: int
        """
        return len(text) > threshold

    @staticmethod
    def _linkedin_url(position: str, location: str) -> List[str]:
        """
        Function which returns the linkedin web page with job offers
        Args:
        - position: job position
        - location: location of the job

        Returns:
        - str: URL with job offer
        """
        return [f"https://www.linkedin.fr/jobs/{position}-jobs-{location}/"]

    @staticmethod
    def _indeed_url(position: str, location: str, number_pages=5) -> List[str]:
        """
        Function which returns the indeed web page with job offers
        Args:
        - position: job position
        - location: location of the job

        Returns:
        - str: URL with job offer
        """
        URL_list = [
            f"https://fr.indeed.com/jobs?q={position}&l={location}&start={str(i)}"
            for i in [k * 10 for k in range(number_pages)]
        ]
        return URL_list

    @staticmethod
    def _hellowork_url(position: str, location: str, number_pages=5) -> List[str]:
        """
        Function which returns the indeed web page with job offers
        Args:
        - position: job position
        - location: location of the job

        Returns:
        - str: URL with job offer
        """
        URL_list = [
            f"https://www.hellowork.com/fr-fr/emploi/recherche.html?k={position}&l={location}&p={str(i+1)}&mode=pagination"
            for i in range(number_pages)
        ]
        return URL_list

    @staticmethod
    def _cadreemploi_url(position: str, location: str, number_pages=5) -> List[str]:
        """
        Function which returns the indeed web page with job offers
        Args:
        - position: job position
        - location: location of the job

        Returns:
        - str: URL with job offer
        """
        URL_list = [
            f"https://www.cadremploi.fr/emploi/liste_offres?motscles={position}&ville={location}&page={str(i+1)}"
            for i in range(number_pages)
        ]
        return URL_list

    @staticmethod
    def _wtj_url(position: str, location: str, number_pages=5) -> List[str]:
        """
        Function which returns the welcome to the jungle web page with job offers
        Args:
        - position: job position
        - location: location of the job

        Returns:
        - str: URL with job offer
        """
        if location.lower() == "paris":
            zip_code = "75000"
        zip_code = "75000"
        URL_list = [
            f"https://www.welcometothejungle.com/fr/pages/emploi-{position}-{location}-{zip_code}?page={str(i+1)}"
            for i in range(number_pages)
        ]
        return URL_list

    @staticmethod
    def _talent_url(position: str, location: str, number_pages=5) -> List[str]:
        """
        Function which returns the talent.com web page with job offers
        Args:
        - position: job position
        - location: location of the job

        Returns:
        - str: URL with job offer
        """
        URL_list = [f"https://fr.talent.com/jobs?k={position}&l={location}&p={str(i+1)}" for i in range(number_pages)]
        return URL_list

    def find_url_list(self, position: str, location: str) -> str:
        """
        Function which return according to the plateform, the position and the location the url to scrap
        Args:
        - position: job position
        - location: location of the job

        Output: url: str"""

        if self.platform == "LinkedIn":
            URL_list = self._linkedin_url(position, location)
            return URL_list
        if self.platform == "Indeed":
            URL_list = self._indeed_url(position, location)
            return URL_list
        if self.platform == "Hello Work":
            URL_list = self._hellowork_url(position, location)
            return URL_list
        if self.platform == "Cadre Emploi":
            URL_list = self._cadreemploi_url(position, location)
            return URL_list
        if self.platform == "Welcome to the Jungle":
            URL_list = self._wtj_url(position, location)
            return URL_list
        if self.platform == "Talent.com":
            URL_list = self._talent_url(position, location)

    def scroll(self, driver: webdriver.Chrome, num_scrolls: int, scroll_pause_time: int):
        """
        Scroll the web page multiple times.

        Args:
            num_scrolls (int): Number of times to scroll the page.
            scroll_pause_time (int): Time in seconds to pause between scrolls.
        """
        for _ in range(num_scrolls):
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                self.logger.info(f"Successfully scrolled ({_ + 1} times)")
                time.sleep(scroll_pause_time)
            except Exception as err:
                self.logger.info("Error while scrolling: %s", err)
                return

    def get_raw_google_links(self, query: str, num_results: int = 2) -> list[str]:
        """
        Get the raw links from a Google search.

        Args:
        - query: google query
        - num_results: Number of results to fetch

        Returns:
        - list: list of URLs from the Google search.
        """
        links = []
        n_pages = 2
        for page in range(1, n_pages):
            query_encoded = quote(query)
            url = f"http://www.google.com/search?q={query_encoded}&start={(page - 1) * 10}"

            try:
                html_content = self.fetch_html(url)
                soup = BeautifulSoup(html_content, "html.parser")
                search_results = soup.find_all("div", class_="yuRUbf")
                for result in search_results:
                    link = result.a.get("href")
                    if "pdf" not in link:
                        links.append(link)
            except Exception as err:
                logger.info("An error occured %s", err)
        return links[:num_results]

    @staticmethod
    def check_if_blocked_by_captcha(html_output: str) -> bool:
        """
        Function to detect if we have been blocked by a captcha
        Args:
        - html_output: str

        Returns:
        - bool: True or False
        """
        if "CAPTCHA" in html_output:
            logger.info("Blocked by Captcha")
            return True
        False

    #    def solve_recaptcha_v2(self, driver: webdriver.Chrome) -> None:
    #        """
    #        Solve recaptcha_V2
    #        """
    #
    #        solver = Recaptcha_Solver(
    #            driver=driver,  # Your Web Driver
    #            ffmpeg_path="",  # Optional. If does not exists, it will automatically download.
    #            log=1,  # If you want to view the progress.
    #        )
    #        solver.solve_recaptcha()#
    #
    #        return

    @staticmethod
    def solve_recaptcha_v2(driver: webdriver.Chrome):
        """Solve recaptcha_V2"""
        solver = RecaptchaSolver(driver=driver)
        recaptcha_iframe = driver.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')
        solver.click_recaptcha_v2(iframe=recaptcha_iframe)
        time.sleep(WAIT_TIME)
