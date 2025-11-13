import re
from typing import Optional


def parse_price_to_float(price_text: str) -> Optional[float]:
    if not price_text:
        return None
    # Keep digits, comma, dot; take first number
    m = re.search(r"[\d,.]+", price_text)
    if not m:
        return None
    raw = m.group(0).replace(",", "")
    try:
        return float(raw)
    except ValueError:
        return None


def parse_weight_to_grams(weight_text: str) -> Optional[float]:
    """
    Handles patterns like:
      - 500 g, 1 kg, 1.5 kg
      - 2 x 50 g, 4x100g
      - Returns total grams if possible else None
    """
    if not weight_text:
        return None
    s = weight_text.lower().replace("grams", "g").replace("kilograms", "kg").strip()

    # Pack pattern: e.g., 2 x 50 g or 2x50g
    pack = re.search(r"(\d+)\s*[xX]\s*(\d+(?:\.\d+)?)\s*g", s)
    if pack:
        n = int(pack.group(1))
        grams = float(pack.group(2))
        return n * grams

    # Single grams
    g = re.search(r"(\d+(?:\.\d+)?)\s*g", s)
    if g:
        return float(g.group(1))

    # Kilograms
    kg = re.search(r"(\d+(?:\.\d+)?)\s*kg", s)
    if kg:
        return float(kg.group(1)) * 1000.0

    # Milliliters (not reliably convertible) -> None
    # ml = re.search(r"(\d+(?:\.\d+)?)\s*ml", s)
    return None


def price_per_100g(price: Optional[float], grams: Optional[float]) -> Optional[float]:
    if price is None or grams is None or grams <= 0:
        return None
    return round((price / grams) * 100.0, 2)


def extract_brand(name: str) -> str:
    if not name:
        return "Unknown"
    # Naive: take first token before a separator
    name = name.strip()
    for sep in [" - ", "|", ",", "("]:
        if sep in name:
            name = name.split(sep)[0].strip()
            break
    return name.split()[0] if name else "Unknown"
