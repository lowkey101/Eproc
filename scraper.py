import os
import csv
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# --- Headless Chrome Setup ---
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
        # TARGET: The No-Captcha URL you found
        url = "https://eproc.rajasthan.gov.in/nicgep/app?page=FrontEndListTendersbyDate&service=page"
        print(f"Scraping direct list: {url}")
        driver.get(url)
        time.sleep(10) # Wait for JS to render the table

        # Find the table and all its rows
        # On this page, the table usually has a specific class or ID
        rows = driver.find_elements(By.XPATH, "//table[contains(@class, 'table')]//tr")
        print(f"Detected {len(rows)} rows.")

        for row in rows[1:11]: # Process top 10 new tenders
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) > 4:
                # The 'Title and Ref No' is usually in the 4th or 5th column
                title_info = cols[4].text.strip().replace("/", "-").replace(" ", "_")
                link_element = cols[4].find_element(By.TAG_NAME, "a")
                pdf_url = link_element.get_attribute("href")
                
                # Download PDF
                filename = f"{folder}/{title_info[:50]}.pdf"
                try:
                    res = requests.get(pdf_url, timeout=20)
                    with open(filename, "wb") as f:
                        f.write(res.content)
                    
                    tenders_data.append({
                        "Date": cols[1].text.strip(),
                        "Title": title_info,
                        "File_Path": filename
                    })
                    print(f"Downloaded: {title_info[:30]}")
                except:
                    print(f"Failed to download PDF for: {title_info[:30]}")

        # Save results to tracking file
        with open("tenders.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["Date", "Title", "File_Path"])
            writer.writeheader()
            writer.writerows(tenders_data)

    finally:
        driver.quit()

if __name__ == "__main__":
    run_scraper()
