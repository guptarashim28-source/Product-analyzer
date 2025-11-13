import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
import re

def get_asin_from_url(url):
    """Extracts the ASIN from an Amazon product URL."""
    match = re.search(r'/(dp|product-reviews)/([A-Z0-9]{10})', url)
    if match:
        return match.group(2)
    return None

def download_review_pages_with_selenium(base_url, num_pages, asin):
    """
    Automates downloading Amazon review pages by simulating clicks on the 'Next page' button.
    Saves pages into a directory named after the product ASIN.
    """
    print("Initializing Chrome browser...")
    
    # --- Setup Chrome Options ---
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # --- Initialize WebDriver ---
    try:
        service = Service() 
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except WebDriverException as e:
        print("\n--- WebDriver Error ---")
        print("Could not start Chrome. Please ensure you have Google Chrome installed.")
        print(f"Error details: {e}")
        return

    # --- Login Step ---
    print("\n--- Action Required: Please Log In ---")
    print("A Chrome window will open. Please log in to your Amazon account on any Amazon page.")
    driver.get("https://www.amazon.in")
    
    input("\n>>> Press Enter in this terminal after you have successfully logged in... ")

    print("\nLogin confirmed! Starting review page downloads...")

    # --- HTML Download Step ---
    product_html_dir = os.path.join('html_pages', asin)
    if not os.path.exists(product_html_dir):
        os.makedirs(product_html_dir)

    # Start at the base URL for the reviews
    print(f"Navigating to starting page: {base_url}")
    driver.get(base_url)

    for page_num in range(1, num_pages + 1):
        print(f"Processing page {page_num}...")
        
        try:
            # Wait for the main review container to be visible
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "cm_cr-review_list"))
            )
            time.sleep(2) # Extra wait for dynamic content

            # Save the page source
            file_path = os.path.join(product_html_dir, f'reviews_page_{page_num}.html')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print(f"Successfully saved page {page_num} to {file_path}")

            # If this is the last page we need, don't try to click next
            if page_num == num_pages:
                break

            # Find and click the "Next page" button
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "li.a-last a"))
            )
            print("Clicking 'Next page' button...")
            driver.execute_script("arguments[0].click();", next_button)
            
        except TimeoutException:
            print(f"Could not find the 'Next page' button or review list on page {page_num}. This might be the last page of reviews.")
            break
        except NoSuchElementException:
            print(f"The 'Next page' button was not found on page {page_num}. Assuming it's the last page.")
            break
        except Exception as e:
            print(f"An unexpected error occurred on page {page_num}: {e}")
            break
            
    print("\nFinished downloading all pages.")
    driver.quit()

def main():
    """
    Main function to get user input and start the download process.
    """
    base_url = input("Enter the base URL of the Amazon product reviews page (e.g., https://www.amazon.in/product-reviews/ASIN/...): ")
    
    asin = get_asin_from_url(base_url)
    if not asin:
        print("Could not automatically extract ASIN from the URL.")
        asin = input("Please enter the 10-character product ASIN manually: ")
        if not (len(asin) == 10 and asin.isalnum()):
            print("Invalid ASIN. Aborting.")
            return
    
    print(f"Detected ASIN: {asin}")

    while True:
        try:
            num_pages_str = input("Enter the number of pages you want to download: ")
            num_pages = int(num_pages_str)
            if num_pages > 0:
                break
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a number.")
            
    download_review_pages_with_selenium(base_url, num_pages, asin)
    print("\nDownload process complete.")
    print("You can now run the amazon_scraper.py script to parse the saved HTML files.")

if __name__ == '__main__':
    main()
