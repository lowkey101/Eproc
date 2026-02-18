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

# --- Browser Options for GitHub Actions ---
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

def run_deep_scraper():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    tenders_data = []

    try:
        # Step 1: Access the No-Captcha List
        url = "https://eproc.rajasthan.gov.in/nicgep/app?page=FrontEndListTendersbyDate&service=page"
        driver.get(url)
        
        # Explicit wait for the main table to render
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.ID, "table")))
        
        # Get up to 10 detail links
        links = [el.get_attribute("href") for el in driver.find_elements(By.TAG_NAME, "a") if "FrontEndViewTender" in el.get_attribute("href")][:10]
        print(f"Found {len(links)} tenders to analyze.")

        # Step 2: Visit each Detail Page
        for link in links:
            driver.get(link)
            time.sleep(5) # Wait for Work Item Details table
            
            try:
                # Targeted extraction based on your screenshots
                row_data = {
                    "Tender_ID": driver.find_element(By.XPATH, "//*[contains(text(), 'Tender ID')]/following-sibling::td").text.strip(),
                    "Title": driver.find_element(By.XPATH, "//*[contains(text(), 'Title')]/following-sibling::td").text.strip(),
                    "Value_INR": driver.find_element(By.XPATH, "//*[contains(text(), 'Tender Value')]/following-sibling::td").text.strip().replace(',', ''),
                    "EMD_Amount": driver.find_element(By.XPATH, "//*[contains(text(), 'EMD Amount')]/following-sibling::td").text.strip().replace(',', ''),
                    "Work_Period_Days": driver.find_element(By.XPATH, "//*[contains(text(), 'Period Of Work')]/following-sibling::td").text.strip(),
                    "Submission_End": driver.find_element(By.XPATH, "//*[contains(text(), 'Bid Submission End Date')]/following-sibling::td").text.strip(),
                    "Source_URL": link
                }
                tenders_data.append(row_data)
                print(f"Successfully scraped: {row_data['Tender_ID']}")
            except Exception as e:
                print(f"Skipped a tender due to layout issue: {link}")

        # Step 3: Save to structured CSV
        if tenders_data:
            keys = tenders_data[0].keys()
            with open("tender_details.csv", "w", newline="", encoding="utf-8") as output_file:
                dict_writer = csv.DictWriter(output_file, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerows(tenders_data)

    finally:
        driver.quit()

if __name__ == "__main__":
    run_deep_scraper()
