import json
import os
import signal
import sys
import re
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import pytz
import locale
from urllib.parse import urlparse 

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

locale.setlocale(locale.LC_TIME, "cs_CZ.UTF-8")

# Global flag for thread termination
terminate_flag = threading.Event()

file_lock = threading.Lock()


def signal_handler(sig, frame):
    """
    Handles the termination signal (SIGINT) gracefully by setting a global termination flag.

    Parameters:
    sig (int): Signal number.
    frame (frame object): Current stack frame.
    """
    print("\nTermination signal received, shutting down...")
    terminate_flag.set()
    sys.exit(0)


# Register the signal handler for shutdown (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)


def is_valid_url(url):
    """
    Checks if a given URL is valid.

    Parameters:
    url (str): The URL to validate.

    Returns:
    bool: True if the URL is valid, False otherwise.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def init_chrome_driver():
    """
    Initializes the Chrome WebDriver with specified options.

    Returns:
    WebDriver: Initialized WebDriver instance.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    chrome_options.binary_location = (
        r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    )
    chrome_driver_path = r"C:\Coding\WebDrivers\chromedriver-win64\chromedriver.exe"
    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def getHTML(driver, url, retries=3):
    """
    Fetches the HTML content of a webpage with retries in case of failure.

    Parameters:
    driver (WebDriver): The WebDriver instance.
    url (str): The URL to load.
    retries (int): Number of retry attempts in case of failure.

    Returns:
    str: HTML content of the page.

    Raises:
    Exception: If the page fails to load after the specified number of retries.
    """
    if not is_valid_url(url):
        raise ValueError(f"Invalid URL: {url}")

    for attempt in range(retries):
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            return driver.page_source
        except Exception as e:
            print(f"Error loading page {url} (attempt {attempt + 1}): {e}")
            time.sleep(2)
    raise Exception(f"Failed to load page {url} after {retries} attempts.")


def parse_czech_datetime(datetime_string):
    """
    Parses a datetime string in Czech format.

    Parameters:
    datetime_string (str): The datetime string in Czech format (e.g., "12. října 2024  12:44")

    Returns:
    datetime: A datetime object representing the parsed date and time
    """
    date_part, time_part = datetime_string.strip().rsplit(maxsplit=1)

    czech_months = {
        "ledna": 1,
        "února": 2,
        "března": 3,
        "dubna": 4,
        "května": 5,
        "června": 6,
        "července": 7,
        "srpna": 8,
        "září": 9,
        "října": 10,
        "listopadu": 11,
        "prosince": 12,
    }

    day, month, year = date_part.split()
    day = day.rstrip(".")
    month_num = czech_months[month.lower()]
    hour, minute = map(int, time_part.split(":"))

    return datetime(int(year), month_num, int(day), hour, minute)


def extract_article_data(html):
    """
    Extracts relevant data (title, content, images, comments, etc.) from the HTML of a webpage.

    Parameters:
    html (str): The HTML content of the webpage.

    Returns:
    dict: A dictionary containing the extracted article data.
    """
    soup = BeautifulSoup(html, "html.parser")

    image_count = 0
    img_div = soup.find("div", class_="m-bg-4")
    if img_div:
        image_count = len(img_div.find_all("img"))

    time_date = ""
    time_span = soup.find("span", class_="time-date")
    if time_span:
        time_date = time_span.get_text(strip=True)
        
        try:
            parsed_datetime = parse_czech_datetime(time_date)
            
            prague_tz = pytz.timezone("Europe/Prague")
            localized_datetime = prague_tz.localize(parsed_datetime)
           
            time_date = localized_datetime.isoformat()
        except ValueError as e:
            print(f"Error parsing date: {e}")
            time_date = ""

    title = ""
    headline_h1 = soup.find("h1", itemprop="name headline")
    if headline_h1:
        title = headline_h1.get_text(strip=True)

    article_text = ""
    article_div_opener = soup.find("div", class_="opener")
    if article_div_opener:
        article_text = article_div_opener.get_text(strip=True)

    article_div_text = soup.find("div", class_="text")
    if article_div_text:
        paragraphs = article_div_text.find_all("p")
        h3_tags = article_div_text.find_all("h3", class_="tit")
        additional_text = "\n\n".join(
            [p.get_text(strip=True) for p in paragraphs + h3_tags]
        )
        article_text += "\n\n" + additional_text

    comments_count = 0
    comments_link = soup.find("a", id="moot-linkin")
    if comments_link:
        comments_text = comments_link.get_text(strip=True)
        match = re.search(r"\((\d+)\s*příspěvků\)", comments_text)
        if match:
            comments_count = int(match.group(1))

    return {
        "title": title,
        "article_text": article_text,
        "image_count": image_count,
        "time_date": time_date,
        "comments_count": comments_count,
    }


def save_article_to_json(article_data, category, link, file_name="articles_data.json"):
    """
    Saves article data to a JSON file, ensuring atomic write and thread safety.

    Parameters:
    article_data (dict): The data of the article to be saved.
    category (str): The category of the article.
    link (str): The URL of the article.
    file_name (str): The JSON file to save the data (default is 'articles_data.json').
    """
    with file_lock:
        try:
            if os.path.exists(file_name):
                with open(file_name, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = []

            if not isinstance(data, list):
                print(
                    f"Expected a list in {file_name}, found something else. Creating a new list."
                )
                data = []

            article_title = article_data.get("title", "").strip()
            if not article_title:
                article_title = f"(No title, URL: {link})"

            if any(
                article.get("title") == article_data.get("title") for article in data
            ):
                print(f"Article '{article_title}' already exists, skipped.")
                return

            article_data["category"] = category
            data.append(article_data)

            temp_file = file_name + ".tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            os.replace(temp_file, file_name)
            print(f"Article '{article_title}' saved to {file_name}")

        except Exception as e:
            print(f"Error saving article '{article_title}' to {file_name}: {e}")


def process_article(driver, link, category):
    """
    Processes a single article by loading its page, extracting data, and saving it.

    Parameters:
    driver (WebDriver): The WebDriver instance to use.
    link (str): The URL of the article.
    category (str): The category of the article.

    Returns:
    bool: True if the article was processed successfully, False otherwise.
    """
    try:
        print(f"Processing article: {link}")
        html_content = getHTML(driver, link)
        article_data = extract_article_data(html_content)
        save_article_to_json(article_data, category, link)
        print(f"Successfully processed article: {link}")
        return True
    except Exception as e:
        print(f"Error processing article {link}: {e}")
        return False


def load_article_links(file_name="article_links.json"):
    """
    Loads article links from a JSON file.

    Parameters:
    file_name (str): The JSON file to load the links from (default is 'article_links.json').

    Returns:
    list: A list of article links.
    """
    with open(file_name, "r", encoding="utf-8") as f:
        return json.load(f)


def save_article_links(article_links, file_name="article_links.json"):
    """
    Saves article links to a JSON file.

    Parameters:
    article_links (list): A list of article links to save.
    file_name (str): The JSON file to save the links to (default is 'article_links.json').
    """
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(article_links, f, ensure_ascii=False, indent=4)


def process_articles(max_workers=14):
    """
    Initiates multithreaded processing of articles using multiple WebDriver instances.

    Parameters:
    max_workers (int): The maximum number of threads to use (default is 14).
    """
    article_links = load_article_links()

    print(f"Starting multithreaded article scraping with {max_workers} threads...")
    print(f"Total articles to process: {len(article_links)}")

    lock = threading.Lock()

    def thread_worker():
        driver = init_chrome_driver()
        try:
            while not terminate_flag.is_set():
                with lock:
                    if not article_links:
                        break
                    article_data = article_links.pop(0)

                    if article_data.get("processed", False):
                        continue

                    link = article_data.get("link")
                    category = article_data.get("category")

                if link and category:
                    if process_article(driver, link, category):
                        with lock:
                            article_data["processed"] = True
                            save_article_links(article_links)
        finally:
            driver.quit()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(lambda _: thread_worker(), range(max_workers))


def load_articles_from_json(file_name="articles_data.json"):
    """
    Loads articles data from a JSON file.

    Parameters:
    file_name (str): The JSON file to load the articles from (default is 'articles_data.json').

    Returns:
    list: A list of articles, or an empty list if the file is not found or invalid.
    """
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError(f"Expected a list in {file_name}, found {type(data)}")

        print(f"Successfully loaded {len(data)} articles from {file_name}")
        return data
    except FileNotFoundError:
        print(f"File {file_name} not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {file_name}")
        return []
    except Exception as e:
        print(f"An error occurred while loading from {file_name}: {e}")
        return []


def main():
    """
    Main function that initiates article processing in multithreaded mode.
    """
    try:
        process_articles()
    except Exception as e:
        print(f"An error occurred in the main function: {e}")
        import traceback

        traceback.print_exc()
    finally:
        terminate_flag.set()


if __name__ == "__main__":
    main()
