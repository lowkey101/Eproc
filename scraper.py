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
# Mask the scraper as a real browser to avoid blocks
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

def run_scraper():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    tenders_data = []
    folder = "bid_documents"
    
    if not os.path.exists(folder):
        os.makedirs(folder)

    try:
        url = "https://eproc.rajasthan.gov.in/nicgep/app?page=FrontEndLatestActiveTenders&service=page"
        print(f"Opening: {url}")
        driver.get(url)

        # 1. WAIT: Specifically look for the tender table by ID
        try:
            wait = WebDriverWait(driver, 40)
            wait.until(EC.presence_of_element_located((By.ID, "table")))
            print("Table loaded.")
        except:
            print("Timeout: Table didn't load. Taking screenshot for debug.")
            driver.save_screenshot("debug_error.png")
            return

        # 2. EXTRACT: Get all rows in the body
        rows = driver.find_elements(By.XPATH, "//table[@id='table']/tbody/tr")
        print(f"Detected {len(rows)} rows.")

        for row in rows[:8]: # Just the first 8 for testing
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) > 4:
                title_text = cols[4].text.strip().replace("/", "-").replace(" ", "_")
                # Find the actual download link
                try:
                    link_element = cols[4].find_element(By.TAG_NAME, "a")
                    pdf_url = link_element.get_attribute("href")
                    
                    filename = f"{title_text}.pdf"
                    filepath = os.path.join(folder, filename)
                    
                    # 3. DOWNLOAD
                    res = requests.get(pdf_url, timeout=30)
                    with open(filepath, "wb") as f:
                        f.write(res.content)
                    
                    tenders_data.append({
                        "Date": cols[1].text.strip(),
                        "Title": title_text,
                        "Local_Path": filepath
                    })
                    print(f"Success: {filename}")
                except:
                    print(f"Skipping row: No link found.")

        # 4. SAVE CSV metadata
        if tenders_data:
            with open("tenders.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["Date", "Title", "Local_Path"])
                writer.writeheader()
                writer.writerows(tenders_data)

    finally:
        driver.quit()

if __name__ == "__main__":
    run_scraper()
