import os
import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- Configuration ---
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

def run_deep_scraper():
    # 1. HEARTBEAT: Create empty file so Git doesn't error out
    with open("tender_details.csv", "a", encoding="utf-8"): os.utime("tender_details.csv", None)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    tenders_data = []

    try:
        # 2. NAVIGATE: Use the no-CAPTCHA bypass URL
        url = "https://eproc.rajasthan.gov.in/nicgep/app?page=FrontEndListTendersbyDate&service=page"
        driver.get(url)
        
        # Wait up to 45 seconds for the PWD table to render
        wait = WebDriverWait(driver, 45)
        wait.until(EC.presence_of_element_located((By.ID, "table")))
        
        # 3. COLLECT: Grab links from the first page
        rows = driver.find_elements(By.XPATH, "//table[@id='table']//tr")[1:11]
        detail_links = []
        for row in rows:
            try:
                link = row.find_element(By.TAG_NAME, "a").get_attribute("href")
                detail_links.append(link)
            except: continue

        # 4. CRAWL: Visit each detail page for engineering data
        for link in detail_links:
            driver.get(link)
            time.sleep(5) 
            
            try:
                # Targeted XPaths for Rajasthan PWD portal labels
                row_data = {
                    "Tender_ID": driver.find_element(By.XPATH, "//*[contains(text(), 'Tender ID')]/following-sibling::td").text.strip(),
                    "Title": driver.find_element(By.XPATH, "//*[contains(text(), 'Title')]/following-sibling::td").text.strip(),
                    "Value_INR": driver.find_element(By.XPATH, "//*[contains(text(), 'Tender Value')]/following-sibling::td").text.strip().replace(',', ''),
                    "EMD_Amount": driver.find_element(By.XPATH, "//*[contains(text(), 'EMD Amount')]/following-sibling::td").text.strip().replace(',', ''),
                    "Work_Period": driver.find_element(By.XPATH, "//*[contains(text(), 'Period Of Work')]/following-sibling::td").text.strip(),
                    "Submission_End": driver.find_element(By.XPATH, "//*[contains(text(), 'Bid Submission End Date')]/following-sibling::td").text.strip(),
                    "Source_URL": link
                }
                tenders_data.append(row_data)
                print(f"Captured: {row_data['Tender_ID']}")
            except:
                print(f"Skipping page: Layout mismatch or blocked")

        # 5. SAVE: Write final results
        if tenders_data:
            keys = tenders_data[0].keys()
            with open("tender_details.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(tenders_data)

    finally:
        driver.quit()

if __name__ == "__main__":
    run_deep_scraper()
