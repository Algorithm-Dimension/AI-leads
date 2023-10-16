from selenium import webdriver
from bs4 import BeautifulSoup
import time

def get_webpage_source(url, wait_time=5):
    """
    Get the HTML source of a webpage using Selenium with anti-scraping measures.

    Parameters:
    - url: str, The URL of the webpage to fetch.
    - wait_time: int, The time to wait for the page to load.

    Returns:
    - str: The HTML source of the webpage.
    """
    # Configuration du navigateur avec des en-têtes et un agent utilisateur simulés
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')  # Ajoutez cette option pour éviter les erreurs sur certains systèmes
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
    
    # Configuration du navigateur avec un proxy (facultatif)
    # options.add_argument('--proxy-server=http://your-proxy-server.com:port')

    with webdriver.Chrome(options=options) as driver:
        try:
            driver.get(url)
            # Attente explicite pour laisser la page se charger complètement
            time.sleep(wait_time)
            return driver.page_source
        except Exception as e:
            print(f"Une erreur s'est produite : {str(e)}")
            return None


def extract_readable_text_from_html(html):
    """
    Extract readable text from an HTML string using BeautifulSoup.

    Parameters:
    - html: str, The HTML string.

    Returns:
    - str: The extracted readable text.
    """
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    return ' '.join(text.split())


def extract_readable_text(url):
    """
    Scrapps job search results from a career website.
    """
    try:
        html_source = get_webpage_source(url)
        return extract_readable_text_from_html(html_source)
    except Exception as e:
        print("An error occured :", str(e))
        return None

