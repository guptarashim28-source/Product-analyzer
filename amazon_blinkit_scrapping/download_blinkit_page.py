import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

def save_blinkit_page_with_selenium(url):
    """
    Automates opening a Blinkit page, scrolling to the bottom, and saving the HTML.
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
        return

    # --- Location Setting Step ---
    print("\n--- Action Required: Please Set Your Location ---")
    print("A Chrome window will open. Please enter your pincode or select your location on the Blinkit website.")
    driver.get(url)
    
    input("\n>>> Press Enter in this terminal after you have set your location... ")

    print("\nLocation confirmed! Scrolling to load all products...")

    # --- Scroll to load all products ---
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Wait for new products to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    print("Finished scrolling. Saving the page HTML...")

    # --- Save the fully loaded page source ---
    try:
        with open('blinkit_products.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("Successfully saved the page to blinkit_products.html")
    except Exception as e:
        print(f"An error occurred while saving the file: {e}")

    driver.quit()

def main():
    """
    Main function to get user input.
    """
    url = input("Enter the Blinkit URL you want to download (e.g., a category or search page): ")
    if "blinkit.com" not in url:
        print("Invalid URL. Please provide a valid Blinkit URL.")
        return
        
    save_blinkit_page_with_selenium(url)
    print("\nDownload process complete.")
    print("You can now run the blinkit_scraper.py script to parse the saved HTML file.")

if __name__ == '__main__':
    main()
