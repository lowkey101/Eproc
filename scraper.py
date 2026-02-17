from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

chrome_options = Options()
chrome_options.add_argument("--headless") # Essential for server environments
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

def run_scraper():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    try:
        driver.get("https://eproc.rajasthan.gov.in/nicgep/app?page=FrontEndLatestActiveTenders&service=page")
        time.sleep(5)
        print(f"Title: {driver.title}")
        # Add your extraction logic here
    finally:
        driver.quit()

if __name__ == "__main__":
    run_scraper()
