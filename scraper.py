import os
import time
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth

# Configuration for organized storage
BASE_PATH = "Tenders/JDA"
os.makedirs(BASE_PATH, exist_ok=True)

def run_scraper():
    with sync_playwright() as p:
        # Launching chromium
        browser = p.chromium.launch(headless=True) 
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            accept_downloads=True
        )
        page = context.new_page()
        
        # Correct stealth usage
        stealth(page)

        print("Navigating to JDA Tender List...")
        # JDA Specific Organization Link
        jda_url = "https://eproc.rajasthan.gov.in/nicgep/app?component=%24DirectLink&page=FrontEndTendersByOrganisation&service=direct"
        
        try:
            page.goto(jda_url, wait_until="networkidle")
            # The portal often requires a moment to handle JSF viewstates
            page.wait_for_selector("table.table-bordered", timeout=30000)

            # Locate rows in the tender table
            rows = page.query_selector_all("tr")
            
            for index, row in enumerate(rows[1:]):  # Skip header
                cols = row.query_selector_all("td")
                if len(cols) < 5: continue

                # Extraction
                tender_title = cols[3].inner_text().strip()
                tender_id = cols[4].inner_text().strip().replace("/", "_")
                closing_date = cols[5].inner_text().strip()

                # Directory setup
                folder_path = os.path.join(BASE_PATH, f"{tender_id}")
                os.makedirs(folder_path, exist_ok=True)

                # Save basic info
                with open(os.path.join(folder_path, "info.txt"), "w") as f:
                    f.write(f"Title: {tender_title}\nID: {tender_id}\nClosing: {closing_date}")

                print(f"Stored: {tender_id}")

        except Exception as e:
            print(f"Error during scraping: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run_scraper()
