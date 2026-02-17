import os
import csv
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# --- Headless Browser Configuration ---
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

def run_scraper():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    tenders = []
    folder = "bid_documents"
    
    if not os.path.exists(folder):
        os.makedirs(folder) # Create folder for PDFs

    try:
        url = "https://eproc.rajasthan.gov.in/nicgep/app?page=FrontEndLatestActiveTenders&service=page"
        driver.get(url)
        time.sleep(7) # Required for Rajasthan portal JS loading
        
        rows = driver.find_elements("tag name", "tr")
        for row in rows[1:6]: # Testing with top 5 tenders
            cols = row.find_elements("tag name", "td")
            if len(cols) > 4:
                # Clean title for filename
                title = cols[4].text.strip().replace("/", "-").replace(" ", "_")
                link_element = cols[4].find_element("tag name", "a")
                pdf_url = link_element.get_attribute("href")
                
                # Download the PDF
                try:
                    res = requests.get(pdf_url, timeout=15)
                    filename = f"{folder}/{title}.pdf"
                    with open(filename, "wb") as f:
                        f.write(res.content)
                    tenders.append({"Date": cols[1].text, "Title": title, "File": filename})
                except Exception as e:
                    print(f"Failed to download {title}: {e}")

        # Save metadata to CSV
        with open("tenders.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["Date", "Title", "File"])
            writer.writeheader()
            writer.writerows(tenders)

    finally:
        driver.quit()

if __name__ == "__main__":
    run_scraper()
