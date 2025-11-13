import os
from bs4 import BeautifulSoup
import pandas as pd

def get_soup_from_file(file_path):
    """
    Given a local HTML file path, return a BeautifulSoup object.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup
    except FileNotFoundError:
        print(f"Error: The file was not found at {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None

def get_reviews(soup):
    """
    Given a BeautifulSoup object, return a list of reviews.
    This function is updated based on the selectors from the provided article.
    """
    reviews = []
    # Try to find review containers using a common data-hook
    review_elements = soup.find_all('div', {'data-hook': 'review'})

    # If the above doesn't work, try a selector for review containers based on the article's screenshots.
    if not review_elements:
        review_elements = soup.select('div[id^="customer_review-"]')

    for item in review_elements:
        # Using selectors from the article, with checks for missing elements
        name_element = item.find('span', class_='a-profile-name')
        rating_element = item.find('i', class_='review-rating')
        title_element = item.find('a', class_='review-title')
        body_element = item.find('span', class_='review-text')
        date_element = item.find('span', class_='review-date')

        # Clean up the title text which often contains the rating
        if title_element:
            title_text = title_element.text.strip()
            if '\n' in title_text:
                title_text = title_text.split('\n')[-1].strip()
        else:
            title_text = 'N/A'

        review = {
            'product_title': soup.title.text.replace('Amazon.in:Customer reviews: ', '').strip(),
            'name': name_element.text.strip() if name_element else 'N/A',
            'rating': rating_element.text.strip() if rating_element else 'N/A',
            'title': title_text,
            'review_body': body_element.text.strip() if body_element else 'N/A',
            'review_date': date_element.text.strip() if date_element else 'N/A',
        }
        reviews.append(review)
    return reviews

def main():
    """
    Main function to scrape reviews from locally saved HTML files for each product.
    """
    base_html_dir = 'html_pages'

    if not os.path.exists(base_html_dir):
        print(f"The directory '{base_html_dir}' does not exist. Please run the download_pages.py script first.")
        return

    # Get a list of all product directories (ASINs)
    product_dirs = [d for d in os.listdir(base_html_dir) if os.path.isdir(os.path.join(base_html_dir, d))]

    if not product_dirs:
        print("No product folders found in 'html_pages'. Please run the download script.")
        return

    for asin in product_dirs:
        print(f"\n--- Processing product ASIN: {asin} ---")
        product_html_dir = os.path.join(base_html_dir, asin)
        all_reviews = []

        # Iterate over all saved HTML files for the current product
        for filename in sorted(os.listdir(product_html_dir)):
            if filename.endswith('.html'):
                file_path = os.path.join(product_html_dir, filename)
                print(f"Parsing {file_path}...")
                
                soup = get_soup_from_file(file_path)
                if soup:
                    reviews_on_page = get_reviews(soup)
                    if reviews_on_page:
                        all_reviews.extend(reviews_on_page)
                        print(f"Found {len(reviews_on_page)} reviews on this page.")
                    else:
                        print("No reviews found on this page.")
        
        if all_reviews:
            df = pd.DataFrame(all_reviews)
            # Remove duplicate reviews before saving
            df.drop_duplicates(subset=['name', 'review_date', 'title', 'review_body'], keep='first', inplace=True)
            
            # Save to a product-specific CSV file
            output_csv_path = f'{asin}_reviews.csv'
            df.to_csv(output_csv_path, index=False)
            print(f"\nSuccessfully scraped a total of {len(df)} unique reviews and saved to {output_csv_path}")
        else:
            print(f"\nNo reviews were found for ASIN {asin}.")

if __name__ == '__main__':
    main()
