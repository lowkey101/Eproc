import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# --- Setup Headless Chrome ---
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

def run_scraper():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    tenders = []
    
    try:
        url = "https://eproc.rajasthan.gov.in/nicgep/app?page=FrontEndLatestActiveTenders&service=page"
        driver.get(url)
        time.sleep(5) # Allow JS to load
        
        # Example Logic: Finding rows in the tender table
        # You can refine the CSS_SELECTOR based on actual table IDs
        rows = driver.find_elements("tag name", "tr")
        for row in rows[1:11]: # Scrape top 10 for testing
            cols = row.find_elements("tag name", "td")
            if len(cols) > 4:
                tenders.append({
                    "Date": cols[1].text,
                    "Title": cols[4].text,
                    "Department": "Rajasthan Government"
                })
        
        # --- Save Data to CSV ---
        keys = tenders[0].keys() if tenders else ["Date", "Title", "Department"]
        with open("tenders.csv", "w", newline="", encoding="utf-8") as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(tenders)
            
        print(f"Successfully saved {len(tenders)} tenders to tenders.csv")

    finally:
        driver.quit()

if __name__ == "__main__":
    run_scraper()
