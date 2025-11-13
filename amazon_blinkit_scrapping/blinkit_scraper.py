import pandas as pd
from bs4 import BeautifulSoup

def scrape_blinkit_from_local_html(file_path):
    """
    Scrapes product information from a locally saved Blinkit HTML file.
    """
    print(f"Reading and parsing the local HTML file: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found. Please save the Blinkit page with this name.")
        return
    
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
                # Updated selectors based on the new HTML structure with Tailwind CSS classes
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

    # --- Save data to CSV ---
    if products:
        df = pd.DataFrame(products)
        df.to_csv('blinkit_products.csv', index=False)
        print(f"\nSuccessfully scraped {len(products)} products and saved to blinkit_products.csv")
    else:
        print("\nNo products were found in the HTML file. The page structure may have changed or the file might be incorrect.")

def main():
    """
    Main function to initiate scraping from a local file.
    """
    file_path = 'blinkit_products.html'
    print("--- Blinkit Local HTML Scraper ---")
    print(f"Please make sure you have saved the Blinkit page as '{file_path}' in this directory.")
    input("Press Enter to start scraping...")
    
    scrape_blinkit_from_local_html(file_path)

if __name__ == '__main__':
    main()
