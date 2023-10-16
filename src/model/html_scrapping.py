from selenium import webdriver
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def change_page_indeed(driver, url, i, wait_time=5):
    """
    Click the "Page i" button on a webpage using Selenium.

    Parameters:
    - driver: live selenium webdriver 
    - url: str, The URL of the webpage containing the "Page i" button.
    - i : int, number of the page where we want to go
    - wait_time: int, The time to wait for the page to load.

    Returns:
    - bool: True if the button was successfully clicked, False otherwise.
    """

    # Configuration du navigateur avec un proxy (facultatif)
    # options.add_argument('--proxy-server=http://your-proxy-server.com:port')
    i = str(i)
    try:
        driver.get(url)
        # Attente explicite pour laisser la page se charger complètement
        WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f'a[data-testid="pagination-page-{i}"]'))
        )
        
        # Trouvez l'élément du bouton "Page 2" par l'attribut data-testid
        change_page_button = driver.find_element(By.CSS_SELECTOR, f'a[data-testid="pagination-page-{i}"]')

        # Scroller jusqu'à l'élément
        driver.execute_script("arguments[0].scrollIntoView();", change_page_button)
        
        # Cliquez sur le bouton "Page 2"
        change_page_button.click()

        # Attendez un certain temps pour que la page i se charge (ajustez si nécessaire)
        time.sleep(wait_time)

        # Vous pouvez ajouter ici une vérification pour confirmer que vous êtes sur la page i
        # par exemple, en vérifiant l'URL ou le contenu de la page

        return True
    except Exception as e:
        print(f"Une erreur s'est produite : {str(e)}")
        return False


def scroll(driver, num_scrolls=3, scroll_pause_time=2):
    """
    Scroll down a webpage using Selenium.

    Parameters:
    - driver: WebDriver instance.
    - num_scrolls: int, The number of times to scroll down the page.
    - scroll_pause_time: int, The time to pause between each scroll action (in seconds).
    """
    for _ in range(num_scrolls):
        # Execute JavaScript to scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Pause to let content load after each scroll
        time.sleep(scroll_pause_time)



def get_webpage_source(url, wait_time=5, num_scrolls=30, scroll_pause_time=2):
    """
    Get the HTML source of a webpage with scrolling using Selenium.

    Parameters:
    - url: str, The URL of the webpage to fetch.
    - wait_time: int, The time to wait for the page to load.
    - num_scrolls: int, The number of times to scroll down the page.
    - scroll_pause_time: int, The time to pause between each scroll action (in seconds).

    Returns:
    - str: The HTML source of the webpage.
    """
    # Configuration du navigateur avec des en-têtes et un agent utilisateur simulés
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
    
    # Configuration du navigateur avec un proxy (facultatif)
    # options.add_argument('--proxy-server=http://your-proxy-server.com:port')

    with webdriver.Chrome(options=options) as driver:
        try:
            driver.get(url)
            # Attente explicite pour laisser la page se charger complètement
            time.sleep(wait_time)

            # Scroll down the page
            scroll(driver, num_scrolls, scroll_pause_time)

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

