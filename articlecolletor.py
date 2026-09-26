# articlecollector.py
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time 

# Initialize Chrome driver
def init_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    chrome_driver_path = r"C:\Coding\WebDrivers\chromedriver-win64\chromedriver.exe"
    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Get HTML with retries
def getHTML(driver, url, first_page=False, retries=3):
    for attempt in range(retries):
        try:
            driver.get(url)
            if first_page:
                try:
                    agree_button = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "contentwall_ok"))
                    )
                    agree_button.click()
                except Exception as e:
                    print(f"'Agree and Continue' button not found: {e}")
                try:
                    agree_cookies = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.ID, "didomi-notice-agree-button"))
                    )
                    agree_cookies.click()
                except Exception as e:
                    print(f"Cookies button not found: {e}")
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            return driver.page_source
        except Exception as e:
            print(f"Error loading page {url} (attempt {attempt + 1}): {e}")
            time.sleep(2)
    raise Exception(f"Failed to load page {url} after {retries} attempts.")

# Scrape category links
def getCatLinks(html):
    soup = BeautifulSoup(html, "html.parser")
    menu = soup.find("ul", class_="iph-menu1")
    if not menu:
        print("Menu not found.")
        return []
    links = []
    submenu = menu.find("ul", class_="iph-menu2")
    if submenu:
        for li in submenu.find_all("li"):
            a_tag = li.find("a", {"score-place": "3"})
            if a_tag:
                link = a_tag["href"]
                if link.startswith("/"):
                    link = f"https://www.idnes.cz{link}"
                title = a_tag["title"]
                links.append((link, title))
    else:
        print("Submenu not found.")
    return links

# Scrape article links from a page
def get_article_links_from_page(html):
    soup = BeautifulSoup(html, "html.parser")
    article_links = []
    for a_tag in soup.find_all("a", {"score-type": "Article"}):
        href = a_tag["href"]
        if href.startswith("/"):
            href = f"https://www.idnes.cz{href}"
        article_links.append(href)
    return article_links

# Save article links to a JSON file, avoiding duplicates
def save_article_links(article_links, category_title, seen_links, file_name="article_links.json"):
    if not os.path.exists(file_name):
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump([], f)

    with open(file_name, 'r+', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []

        # Append new links with category, avoiding duplicates
        for article_link in article_links:
            if article_link not in seen_links:
                data.append({"link": article_link, "category": category_title})
                seen_links.add(article_link)

        f.seek(0)
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.truncate()

    print(f"Article links saved to {file_name}")

# Load existing links from the JSON file
def load_existing_links(file_name="article_links.json"):
    seen_links = set()
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                for entry in data:
                    seen_links.add(entry["link"])
            except json.JSONDecodeError:
                print("Error reading JSON file. Starting with an empty set.")
    return seen_links

# Get article links from a category (without multithreading)
def get_category_article_links(driver, category_link, category_title, seen_links):
    category_articles = []
    print(f"Scraping category: {category_title} - {category_link}")
    
    for page in range(1, 400):  # Loop through pages 1 to 120
        paginated_link = f"{category_link}/{page}"  # Construct the paginated URL
        try:
            html_content = getHTML(driver, paginated_link)
            article_links = get_article_links_from_page(html_content)

            if not article_links:
                print(f"No more articles found on page {page} for category '{category_title}'.")
                break
            
            category_articles.extend(article_links)
            print(f"Found {len(article_links)} articles on page {page} in category '{category_title}'.")

            # Save links live
            save_article_links(article_links, category_title, seen_links)

        except Exception as e:
            print(f"Error scraping page {page} of category '{category_title}': {e}")
            break  # Exit loop on error

    return category_articles

# Main function to collect categories and article links
def main():
    url = "https://www.idnes.cz/"
    driver = init_chrome_driver()
    seen_links = load_existing_links()

    try:
        html_content = getHTML(driver, url, first_page=True)
        categories = getCatLinks(html_content)

        if categories:
            print(f"Found {len(categories)} categories.")
        else:
            print("No categories found!")

        for category_link, category_title in categories:
            get_category_article_links(driver, category_link, category_title, seen_links)

    except Exception as e:
        print(f"An error occurred in the main function: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
