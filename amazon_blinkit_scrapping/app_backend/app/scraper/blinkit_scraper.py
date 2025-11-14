import time
import os
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import quote_plus

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ..utils.weights import parse_price_to_float, parse_weight_to_grams, price_per_100g, extract_brand


SEARCH_URL_TPL = "https://blinkit.com/s/?q={query}"


def _init_driver(headless: bool = True) -> webdriver.Chrome:
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    # Allow overriding headless via env var BLINKIT_HEADLESS=0/false
    headless_env = os.getenv("BLINKIT_HEADLESS", "1").lower()
    headless_flag = headless if headless_env not in ("0", "false") else False
    if headless_flag:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1400,1000")
    chrome_options.add_argument("--lang=en-IN")
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    )
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_window_size(1400, 1000)
    return driver


def _set_location(driver: webdriver.Chrome, pincode: str, timeout: int = 20) -> bool:
    """
    Best-effort automation to set location/pincode without manual input.
    Returns True if location was successfully set, False otherwise.
    """
    wait = WebDriverWait(driver, timeout)
    
    # Strategy 1: Look for visible input fields with common patterns
    input_patterns = [
        "//input[contains(translate(@placeholder, 'PINCODE', 'pincode'), 'pincode')]",
        "//input[contains(translate(@placeholder, 'PIN', 'pin'), 'pin')]",
        "//input[contains(translate(@placeholder, 'AREA', 'area'), 'area')]",
        "//input[contains(translate(@placeholder, 'LOCATION', 'location'), 'location')]",
        "//input[@type='text' and @name='pincode']",
        "//input[@type='text' and contains(@id, 'pincode')]",
        "//input[@type='text' and contains(@id, 'location')]",
    ]
    
    for pattern in input_patterns:
        try:
            pin_input = driver.find_element(By.XPATH, pattern)
            if pin_input.is_displayed():
                pin_input.clear()
                pin_input.send_keys(pincode)
                time.sleep(0.5)
                pin_input.send_keys(Keys.ENTER)
                time.sleep(3)  # Wait for location to apply
                return True
        except Exception:
            continue
    
    # Strategy 2: Try clicking location-related buttons first
    button_texts = ["Detect", "Location", "Delivery", "Select", "Change"]
    for btn_text in button_texts:
        try:
            # Try exact match
            btn = driver.find_element(By.XPATH, f"//button[contains(text(), '{btn_text}')]")
            if btn.is_displayed():
                btn.click()
                time.sleep(2)
                
                # Now try to find input after modal opens
                for pattern in input_patterns:
                    try:
                        pin_input = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, pattern))
                        )
                        if pin_input.is_displayed():
                            pin_input.clear()
                            pin_input.send_keys(pincode)
                            time.sleep(0.5)
                            pin_input.send_keys(Keys.ENTER)
                            time.sleep(3)
                            return True
                    except Exception:
                        continue
        except Exception:
            continue
    
    # Strategy 3: Try any visible text input as last resort
    try:
        inputs = driver.find_elements(By.XPATH, "//input[@type='text']")
        for inp in inputs:
            if inp.is_displayed():
                inp.clear()
                inp.send_keys(pincode)
                time.sleep(0.5)
                inp.send_keys(Keys.ENTER)
                time.sleep(3)
                return True
    except Exception:
        pass
    
    return False


def _scroll_to_bottom(driver: webdriver.Chrome, max_scrolls: int = 40) -> int:
    last_height = driver.execute_script("return document.body.scrollHeight")
    attempts = 0
    stagnant = 0
    while attempts < max_scrolls:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3.0)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            stagnant += 1
            if stagnant >= 2:
                break
        else:
            stagnant = 0
        last_height = new_height
        attempts += 1
    return attempts


def _extract_first(regex, text: str) -> Optional[str]:
    import re
    m = re.search(regex, text)
    return m.group(0) if m else None


def _parse_products(html: str) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(html, 'html.parser')

    products: List[Dict[str, Any]] = []

    # Try multiple selectors for product cards
    selectors = [
        'div[id][role="button"][tabindex="0"]',
        'div[data-testid*="product"]',
        'div[data-test*="product"]',
        'a[href*="/product/"]',
    ]
    seen = set()
    cards: List[Any] = []
    for sel in selectors:
        for el in soup.select(sel):
            if id(el) not in seen:
                cards.append(el)
                seen.add(id(el))

    # Fallback: broader card guess by presence of price symbol
    if not cards:
        for el in soup.find_all(['div', 'a']):
            txt = el.get_text(" ", strip=True)
            if '₹' in txt and len(txt) < 400:
                cards.append(el)

    for card in cards:
        try:
            name_el = card.select_one("div.tw-text-300.tw-font-semibold.tw-line-clamp-2")
            weight_el = card.select_one("div.tw-text-200.tw-font-medium.tw-line-clamp-1")
            price_el = card.select_one("div.tw-flex.tw-items-center.tw-justify-between > div > div.tw-text-200.tw-font-semibold")

            name = name_el.text.strip() if name_el else ""
            weight = weight_el.text.strip() if weight_el else ""
            price_text = price_el.text.strip() if price_el else ""

            # Fallbacks using regex on the card text
            if not name or len(name) < 3:
                lines = [s.strip() for s in card.get_text("\n", strip=True).split("\n") if s.strip()]
                if lines:
                    name = sorted(lines, key=lambda s: len(s), reverse=True)[0][:120]

            if not weight or len(weight) < 2:
                full_text = card.get_text(" ", strip=True)
                weight = _extract_first(r"\b\d+(?:\.\d+)?\s*(?:x\s*)?\d*(?:\.\d+)?\s*(?:g|kg)\b", full_text) or ""

            if not price_text:
                price_text = _extract_first(r"₹\s*\d[\d,]*(?:\.\d+)?", card.get_text(" ", strip=True)) or ""

            price = parse_price_to_float(price_text)
            grams = parse_weight_to_grams(weight)
            p100 = price_per_100g(price, grams)
            brand = extract_brand(name)

            # Filter out invalid products (search headers, empty products, etc.)
            if (name and len(name) > 5 and 
                not name.lower().startswith('showing') and
                not name.lower().startswith('results for') and
                price is not None and price > 0):
                products.append({
                    "name": name or "N/A",
                    "brand": brand,
                    "weight": weight or "N/A",
                    "price": price,
                    "price_text": price_text,
                    "grams": grams,
                    "price_per_100g": p100
                })
        except Exception:
            continue

    return products


def scrape_for_pincode_query(pincode: str, query: str, save_html: bool = False, max_scrolls: int = 40) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    driver = _init_driver(headless=True)
    try:
        url = SEARCH_URL_TPL.format(query=quote_plus(query))
        driver.get(url)
        time.sleep(3)

        # Try to set location and verify it worked
        location_set = _set_location(driver, pincode)
        
        if not location_set:
            print(f"Warning: Could not automatically set location for pincode {pincode}. Results may be for default location.")
        
        # Force a fresh page load after setting location to ensure results match the pincode
        driver.delete_all_cookies()  # Clear any cached location
        driver.get(url)
        time.sleep(3)
        
        # Try setting location again after reload
        _set_location(driver, pincode)
        time.sleep(2)

        _scroll_to_bottom(driver, max_scrolls=max_scrolls)
        html = driver.page_source

        products = _parse_products(html)

        # Save HTML if requested or no products (for debugging)
        out_dir = os.path.join("html_pages", f"blinkit_{pincode}")
        os.makedirs(out_dir, exist_ok=True)
        html_filename = f"{query.replace(' ', '_')}_{pincode}.html"
        if save_html or not products:
            try:
                with open(os.path.join(out_dir, html_filename), "w", encoding="utf-8") as f:
                    f.write(html)
                print(f"Saved HTML to {out_dir}/{html_filename}")
            except Exception as e:
                print(f"Failed to save HTML: {e}")
        
        print(f"Scraped {len(products)} products for pincode {pincode}, query '{query}'")
        return products, html if save_html else None
    finally:
        try:
            driver.quit()
        except Exception:
            pass
