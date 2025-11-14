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


def _verify_pincode(driver: webdriver.Chrome, expected_pincode: str) -> bool:
    """
    Verify if the displayed pincode matches the expected one
    """
    try:
        verification_methods = []
        
        # Look for pincode display in various locations
        patterns = [
            f"//*[contains(text(), '{expected_pincode}')]",
            f"//span[contains(text(), '{expected_pincode}')]",
            f"//div[contains(text(), '{expected_pincode}')]",
            f"//button[contains(text(), '{expected_pincode}')]",
            f"//input[@value='{expected_pincode}']",
        ]
        
        for pattern in patterns:
            try:
                element = driver.find_element(By.XPATH, pattern)
                if element.is_displayed():
                    verification_methods.append(f"Found in page element: {element.tag_name}")
                    print(f"   ✓ Found pincode {expected_pincode} displayed on page ({element.tag_name})")
                    return True
            except:
                continue
        
        # Check localStorage
        stored_pincode = driver.execute_script("return localStorage.getItem('pincode') || localStorage.getItem('delivery_pincode');")
        if stored_pincode == expected_pincode:
            verification_methods.append("Found in localStorage")
            print(f"   ✓ Pincode {expected_pincode} found in localStorage")
            return True
        elif stored_pincode:
            print(f"   ⚠️ localStorage has different pincode: {stored_pincode}")
        
        # Check sessionStorage
        session_pincode = driver.execute_script("return sessionStorage.getItem('pincode') || sessionStorage.getItem('delivery_pincode');")
        if session_pincode == expected_pincode:
            verification_methods.append("Found in sessionStorage")
            print(f"   ✓ Pincode {expected_pincode} found in sessionStorage")
            return True
        elif session_pincode:
            print(f"   ⚠️ sessionStorage has different pincode: {session_pincode}")
        
        # Check cookies
        try:
            cookies = driver.get_cookies()
            for cookie in cookies:
                if 'pincode' in cookie.get('name', '').lower() or 'location' in cookie.get('name', '').lower():
                    print(f"   🍪 Cookie found: {cookie.get('name')} = {cookie.get('value')}")
                    if expected_pincode in str(cookie.get('value', '')):
                        return True
        except:
            pass
            
        print(f"   ✗ Could not verify pincode {expected_pincode} anywhere")
        return False
    except Exception as e:
        print(f"   ⚠️ Verification error: {e}")
        return False


def _set_location(driver: webdriver.Chrome, pincode: str, timeout: int = 20) -> bool:
    """
    Best-effort automation to set location/pincode without manual input.
    Returns True if location was successfully set, False otherwise.
    """
    wait = WebDriverWait(driver, timeout)
    
    print(f"   🔍 Looking for pincode input field...")
    
    # Strategy 1: Look for visible input fields with common patterns
    input_patterns = [
        "//input[contains(translate(@placeholder, 'PINCODE', 'pincode'), 'pincode')]",
        "//input[contains(translate(@placeholder, 'PIN', 'pin'), 'pin')]",
        "//input[contains(translate(@placeholder, 'AREA', 'area'), 'area')]",
        "//input[contains(translate(@placeholder, 'LOCATION', 'location'), 'location')]",
        "//input[contains(translate(@placeholder, 'DELIVERY', 'delivery'), 'delivery')]",
        "//input[@type='text' and @name='pincode']",
        "//input[@type='text' and contains(@id, 'pincode')]",
        "//input[@type='text' and contains(@id, 'location')]",
        "//input[@type='number' and contains(@placeholder, 'code')]",
    ]
    
    for pattern in input_patterns:
        try:
            pin_input = driver.find_element(By.XPATH, pattern)
            if pin_input.is_displayed():
                print(f"   ✓ Found input field with pattern: {pattern[:50]}...")
                pin_input.clear()
                pin_input.send_keys(pincode)
                time.sleep(0.3)
                pin_input.send_keys(Keys.ENTER)
                time.sleep(2)  # Wait for location to apply
                print(f"   ✅ Pincode {pincode} entered successfully")
                return True
        except Exception as e:
            continue
    
    # Strategy 2: Try clicking location-related buttons first
    print(f"   🔍 Looking for location button...")
    button_texts = ["Detect", "Location", "Delivery", "Select", "Change", "Set"]
    for btn_text in button_texts:
        try:
            # Try exact match
            btn = driver.find_element(By.XPATH, f"//button[contains(text(), '{btn_text}')]")
            if btn.is_displayed():
                print(f"   ✓ Found button: {btn_text}")
                btn.click()
                time.sleep(1.5)
                
                # Now try to find input after modal opens
                for pattern in input_patterns:
                    try:
                        pin_input = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, pattern))
                        )
                        if pin_input.is_displayed():
                            print(f"   ✓ Modal opened, entering pincode...")
                            pin_input.clear()
                            pin_input.send_keys(pincode)
                            time.sleep(0.3)
                            pin_input.send_keys(Keys.ENTER)
                            time.sleep(2)
                            print(f"   ✅ Pincode {pincode} entered via modal")
                            return True
                    except Exception:
                        continue
        except Exception:
            continue
    
    # Strategy 3: Try any visible text input as last resort
    print(f"   🔍 Trying any visible text input...")
    try:
        inputs = driver.find_elements(By.XPATH, "//input[@type='text']")
        for inp in inputs:
            if inp.is_displayed():
                placeholder = inp.get_attribute("placeholder") or ""
                if any(word in placeholder.lower() for word in ["pin", "code", "location", "area", "delivery"]):
                    print(f"   ✓ Found matching input: {placeholder}")
                    inp.clear()
                    inp.send_keys(pincode)
                    time.sleep(0.3)
                    inp.send_keys(Keys.ENTER)
                    time.sleep(2)
                    print(f"   ✅ Pincode {pincode} entered successfully")
                    return True
    except Exception:
        pass
    
    print(f"   ❌ Could not find pincode input field")
    return False


def _scroll_to_bottom(driver: webdriver.Chrome, max_scrolls: int = 20) -> int:
    last_height = driver.execute_script("return document.body.scrollHeight")
    attempts = 0
    stagnant = 0
    while attempts < max_scrolls:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.5)  # Increased from 1.5s for more reliable loading
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            stagnant += 1
            if stagnant >= 3:  # Increased from 2 for better accuracy
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


def scrape_for_pincode_query(pincode: str, query: str, save_html: bool = False, max_scrolls: int = 20, headless: bool = True) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    driver = _init_driver(headless=headless)
    try:
        url = SEARCH_URL_TPL.format(query=quote_plus(query))
        print(f"🌐 Opening Blinkit with query: {query}")
        
        # Try to set geolocation based on pincode (approximate)
        # This won't work for all pincodes but might help
        pincode_coords = {
            "110001": {"latitude": 28.6139, "longitude": 77.2090, "accuracy": 100},  # Delhi
            "400050": {"latitude": 19.0760, "longitude": 72.8777, "accuracy": 100},  # Mumbai
            "560001": {"latitude": 12.9716, "longitude": 77.5946, "accuracy": 100},  # Bangalore
            "380015": {"latitude": 23.0225, "longitude": 72.5714, "accuracy": 100},  # Ahmedabad
        }
        
        if pincode in pincode_coords:
            coords = pincode_coords[pincode]
            print(f"📍 Setting geolocation to {coords['latitude']}, {coords['longitude']}")
            driver.execute_cdp_cmd("Emulation.setGeolocationOverride", coords)
        
        driver.get(url)
        
        if not headless:
            # Manual location mode - give user time to set location
            print(f"\n⏳ Waiting 15 seconds for you to manually set location to {pincode}...")
            print(f"   Click on the location/delivery area on the Blinkit page")
            print(f"   Change it to pincode: {pincode}")
            print(f"   Scraping will continue automatically...\n")
            time.sleep(15)
        else:
            time.sleep(3)  # Increased initial wait

        # Try to set location and verify it worked
        print(f"📍 Attempting to set location to pincode: {pincode}")
        location_set = _set_location(driver, pincode)
        
        if location_set:
            print(f"✅ Location set to pincode {pincode}")
        else:
            print(f"⚠️ Warning: Could not automatically set location for pincode {pincode}.")
            print(f"   Trying alternative method...")
            
            # Alternative: Try to navigate to a URL with location parameter
            try:
                # Some sites accept pincode as URL parameter
                driver.execute_script(f"localStorage.setItem('pincode', '{pincode}');")
                driver.execute_script(f"localStorage.setItem('delivery_pincode', '{pincode}');")
                time.sleep(1)
            except Exception as e:
                print(f"   localStorage attempt failed: {e}")
        
        # Force a fresh page load after setting location to ensure results match the pincode
        print(f"🔄 Reloading page to apply pincode {pincode}...")
        driver.get(url)
        time.sleep(2)
        
        # Try setting location one more time after reload
        if not location_set:
            location_set = _set_location(driver, pincode)
            if location_set:
                print(f"   ✅ Location set successfully on second attempt")
        
        # Verify the pincode is actually applied
        pincode_verified = _verify_pincode(driver, pincode)
        if not pincode_verified:
            print(f"")
            print(f"⚠️⚠️⚠️ WARNING: Could not verify pincode {pincode} is active! ⚠️⚠️⚠️")
            print(f"Products shown may be from default location (380015 or similar)")
            print(f"")
            print(f"💡 SOLUTION: Blinkit requires manual location selection in browser.")
            print(f"   Products scraped will be from whatever location Blinkit defaults to.")
            print(f"   For accurate location-based scraping:")
            print(f"   1. Open Blinkit in a browser manually")
            print(f"   2. Set your delivery location to {pincode}")
            print(f"   3. Note: Automated pincode change has limitations")
            print(f"")
        else:
            print(f"✅ Pincode {pincode} verified and active")
        
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
                print(f"💾 Saved HTML to {out_dir}/{html_filename}")
            except Exception as e:
                print(f"❌ Failed to save HTML: {e}")
        
        # Detailed verification and product logging
        pincode_is_verified = _verify_pincode(driver, pincode)
        print(f"\n{'='*70}")
        print(f"📊 SCRAPING RESULTS SUMMARY")
        print(f"{'='*70}")
        print(f"🔍 Search Query: '{query}'")
        print(f"📍 Requested Pincode: {pincode}")
        
        if pincode_is_verified:
            print(f"✅ Pincode Verified: YES ✅")
            print(f"   Products below are from pincode {pincode}")
        else:
            print(f"⚠️⚠️⚠️ Pincode Verified: NO ⚠️⚠️⚠️")
            print(f"   WARNING: Blinkit did NOT accept the pincode change!")
            print(f"   Products shown are likely from DEFAULT LOCATION (380015 or last-used)")
            print(f"   This is a LIMITATION of Blinkit's website automation.")
            print(f"   Solution: Manually open Blinkit, set location, then scrape.")
        
        print(f"📦 Total Products Found: {len(products)}")
        
        if products:
            print(f"\n📋 FIRST 5 PRODUCTS (for verification):")
            for i, product in enumerate(products[:5], 1):
                print(f"  {i}. {product.get('name', 'N/A')[:60]}")
                print(f"     Brand: {product.get('brand', 'N/A')} | Weight: {product.get('weight', 'N/A')} | Price: ₹{product.get('price', 0)}")
        else:
            print(f"\n⚠️ WARNING: No products found!")
        
        # Check page content for location indicators
        try:
            page_text = driver.find_element(By.TAG_NAME, "body").text
            location_indicators = []
            if pincode in page_text:
                location_indicators.append(f"✓ Pincode {pincode} found in page text")
            if "delivery" in page_text.lower():
                location_indicators.append("✓ 'Delivery' text found on page")
            if "location" in page_text.lower():
                location_indicators.append("✓ 'Location' text found on page")
            
            if location_indicators:
                print(f"\n🔍 PAGE CONTENT ANALYSIS:")
                for indicator in location_indicators:
                    print(f"  {indicator}")
        except:
            pass
        
        print(f"{'='*70}\n")
        
        return products, html if save_html else None
    finally:
        try:
            driver.quit()
        except Exception:
            pass
