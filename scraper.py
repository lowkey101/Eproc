import os
import csv
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
# This makes the bot look like a standard Windows Chrome browser
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

def run_scraper():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    tenders_data = []
    folder = "bid_documents"
    
    if not os.path.exists(folder):
        os.makedirs(folder)

    try:
        # BYPASS URL: This link directly targets the active list without the search form
        url = "https://eproc.rajasthan.gov.in/nicgep/app?page=FrontEndLatestActiveTenders&service=page"
        print(f"Accessing direct list: {url}")
        driver.get(url)

        # Wait for the table to appear (skipping the search form)
        wait = WebDriverWait(driver, 30)
        try:
            # Check for the specific table ID used in the results
            wait.until(EC.presence_of_element_located((By.ID, "table")))
            print("Successfully bypassed CAPTCHA page.")
        except:
            print("Failed to bypass. Portal is demanding CAPTCHA.")
            driver.save_screenshot("bypass_failed.png")
            return

        rows = driver.find_elements(By.XPATH, "//table[@id='table']//tr")
        for row in rows[1:11]: # Scrape top 10
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) > 4:
                title = cols[4].text.strip().replace("/", "-").replace(" ", "_")
                link_el = cols[4].find_element(By.TAG_NAME, "a")
                pdf_url = link_el.get_attribute("href")
                
                # Download using requests to save memory
                res = requests.get(pdf_url, timeout=20)
                filename = f"{folder}/{title}.pdf"
                with open(filename, "wb") as f:
                    f.write(res.content)
                
                tenders_data.append({"Date": cols[1].text, "Title": title, "File": filename})

        # Update CSV
        if tenders_data:
            with open("tenders.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["Date", "Title", "File"])
                writer.writeheader()
                writer.writerows(tenders_data)

    finally:
        driver.quit()

if __name__ == "__main__":
    run_scraper()
