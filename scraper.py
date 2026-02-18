import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def download_tender_files():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    try:
        # 1. Navigate to the specific Tender Detail page
        # Replace with the URL from your screenshot
        detail_url = "https://eproc.rajasthan.gov.in/nicgep/app?page=FrontEndViewTender&service=direct"
        driver.get(detail_url)
        
        print("\n[ACTION REQUIRED]:")
        print("1. Go to the browser window opened by the bot.")
        print("2. Solve the CAPTCHA manually.")
        print("3. DO NOT click download yet.")
        input("4. Press ENTER here in this terminal once the CAPTCHA is solved...")

        # 2. Find and click the PDF download links
        # These are usually in the 'Tenders Documents' or 'Work Item Documents' tables
        pdf_links = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
        
        for i, link in enumerate(pdf_links):
            link.click()
            print(f"Triggered download for file {i+1}")
            time.sleep(2) # Short wait for download to start

        print("Downloads complete. Check your default download folder.")

    finally:
        # Keep browser open for a moment to ensure files finish
        time.sleep(5)
        driver.quit()

if __name__ == "__main__":
    download_tender_files()
