import os
import csv
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# --- Configuration ---
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

def run_scraper():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    tenders_data = []
    folder = "bid_documents"
    
    if not os.path.exists(folder):
        os.makedirs(folder)

    try:
        url = "https://eproc.rajasthan.gov.in/nicgep/app?page=FrontEndLatestActiveTenders&service=page"
        driver.get(url)
        time.sleep(8) # Portal is slow; giving extra time for AJAX
        
        # Locate the results table
        rows = driver.find_elements(By.XPATH, "//table[@id='table']//tr")
        print(f"Detected {len(rows)} rows.")

        for row in rows[1:11]: # Scrape top 10 new tenders
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) > 4:
                # Clean naming convention: TenderID_Title
                date_val = cols[1].text.strip()
                title_text = cols[4].text.strip().replace("/", "-").replace(" ", "_")
                link_element = cols[4].find_element(By.TAG_NAME, "a")
                pdf_url = link_element.get_attribute("href")
                
                # Download PDF
                filename = f"{title_text}.pdf"
                filepath = os.path.join(folder, filename)
                
                try:
                    res = requests.get(pdf_url, timeout=20)
                    with open(filepath, "wb") as f:
                        f.write(res.content)
                    
                    tenders_data.append({
                        "Date": date_val,
                        "Title": title_text,
                        "Local_Path": filepath,
                        "Source_URL": pdf_url
                    })
                    print(f"Downloaded: {filename}")
                except Exception as e:
                    print(f"Failed download for {title_text}: {e}")

        # Save to CSV for tracking
        with open("tenders.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["Date", "Title", "Local_Path", "Source_URL"])
            writer.writeheader()
            writer.writerows(tenders_data)

    finally:
        driver.quit()

if __name__ == "__main__":
    run_scraper()
