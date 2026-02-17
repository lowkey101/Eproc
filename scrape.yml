import os
import csv
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# --- Browser Setup ---
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

def run_scraper():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    tenders = []
    download_folder = "bid_documents"
    
    # Create folder for PDFs
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    try:
        url = "https://eproc.rajasthan.gov.in/nicgep/app?page=FrontEndLatestActiveTenders&service=page"
        driver.get(url)
        time.sleep(7)
        
        rows = driver.find_elements("tag name", "tr")
        for i, row in enumerate(rows[1:6]): # Testing with first 5 tenders
            cols = row.find_elements("tag name", "td")
            if len(cols) > 4:
                title = cols[4].text.replace("/", "-") # Clean filename
                link_element = cols[4].find_element("tag name", "a")
                pdf_url = link_element.get_attribute("href")
                
                # Metadata for CSV
                tenders.append({"Date": cols[1].text, "Title": title, "File": f"{title}.pdf"})
                
                # --- Download PDF ---
                response = requests.get(pdf_url, stream=True)
                if response.status_code == 200:
                    with open(f"{download_folder}/{title}.pdf", "wb") as f:
                        f.write(response.content)
        
        # Save CSV metadata
        if tenders:
            keys = tenders[0].keys()
            with open("tenders.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(tenders)

    finally:
        driver.quit()

if __name__ == "__main__":
    run_scraper()
