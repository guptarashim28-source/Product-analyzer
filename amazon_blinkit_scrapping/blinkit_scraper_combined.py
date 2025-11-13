import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

def download_blinkit_page_with_selenium(url):
    """
    Automates opening a Blinkit page, scrolling to the bottom, and returning the HTML.
    Returns the page source HTML as a string, or None if an error occurred.
    """
    print("Initializing Chrome browser...")
    
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    try:
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except WebDriverException as e:
        print("\n--- WebDriver Error ---")
        print("Could not start Chrome. Please ensure you have Google Chrome installed.")
        print(f"Error details: {e}")
        return None

    # --- Location Setting Step ---
    print("\n--- Action Required: Please Set Your Location ---")
    print("A Chrome window will open. Please enter your pincode or select your location on the Blinkit website.")
    driver.get(url)
    
    input("\n>>> Press Enter in this terminal after you have set your location... ")

    print("\nLocation confirmed! Scrolling to load all products...")

    # --- Scroll to load all products ---
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_attempts = 0
    max_scroll_attempts = 50  # Safety limit to avoid infinite loops
    
    while scroll_attempts < max_scroll_attempts:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Wait for new products to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        scroll_attempts += 1

    print(f"Finished scrolling after {scroll_attempts} attempts.")

    # --- Get the fully loaded page source ---
    page_source = driver.page_source
    driver.quit()
    
    return page_source


def scrape_blinkit_from_html(html_content):
    """
    Scrapes product information from Blinkit HTML content.
    Returns a pandas DataFrame with product data.
    """
    print("Parsing the HTML content...")
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    print("Extracting product data...")
    products = []
    
    # --- Find all product cards ---
    try:
        # The product cards are divs with a unique ID and a role of 'button'
        product_cards = soup.select('div[id][role="button"][tabindex="0"]')
        
        print(f"Found {len(product_cards)} product cards.")

        for card in product_cards:
            try:
                # Updated selectors based on the HTML structure with Tailwind CSS classes
                name_element = card.select_one("div.tw-text-300.tw-font-semibold.tw-line-clamp-2")
                weight_element = card.select_one("div.tw-text-200.tw-font-medium.tw-line-clamp-1")
                # This selector is more specific to get the price and avoid the striked-out price
                price_element = card.select_one("div.tw-flex.tw-items-center.tw-justify-between > div > div.tw-text-200.tw-font-semibold")
                
                name = name_element.text.strip() if name_element else "N/A"
                weight = weight_element.text.strip() if weight_element else "N/A"
                price = price_element.text.strip() if price_element else "N/A"
                
                products.append({
                    'name': name,
                    'weight': weight,
                    'price': price
                })
            except Exception:
                # This handles cases where a card might be an ad or has a different structure
                print("Skipping a card with missing information.")
                continue
    
    except Exception as e:
        print(f"An error occurred while extracting product details: {e}")

    return pd.DataFrame(products) if products else pd.DataFrame()


def main():
    """
    Main function to download and scrape Blinkit data in one go.
    """
    print("=" * 60)
    print("Blinkit Combined Scraper - Download & Parse")
    print("=" * 60)
    
    url = input("\nEnter the Blinkit URL you want to scrape (e.g., a category or search page): ")
    if "blinkit.com" not in url:
        print("Invalid URL. Please provide a valid Blinkit URL.")
        return
    
    # Step 1: Download the page
    print("\n--- Step 1: Downloading Page ---")
    html_content = download_blinkit_page_with_selenium(url)
    
    if not html_content:
        print("Failed to download the page. Exiting.")
        return
    
    # Optional: Save the HTML for backup/debugging
    save_html = input("\nDo you want to save the HTML file? (y/n, default=n): ").strip().lower()
    if save_html == 'y':
        try:
            with open('blinkit_products.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            print("Successfully saved the page to blinkit_products.html")
        except Exception as e:
            print(f"An error occurred while saving the file: {e}")
    
    # Step 2: Parse the HTML
    print("\n--- Step 2: Parsing Product Data ---")
    df = scrape_blinkit_from_html(html_content)
    
    # Step 3: Save to CSV
    if not df.empty:
        output_file = 'blinkit_products.csv'
        df.to_csv(output_file, index=False)
        print(f"\n{'=' * 60}")
        print(f"SUCCESS! Scraped {len(df)} products and saved to {output_file}")
        print(f"{'=' * 60}")
        
        # Show a preview
        print("\nPreview of the first 5 products:")
        print(df.head().to_string(index=False))
    else:
        print("\nNo products were found. The page structure may have changed or the URL might be incorrect.")
    
    print("\nScraping complete!")


if __name__ == '__main__':
    main()
