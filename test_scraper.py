import requests
import json

print("="*70)
print("TESTING BLINKIT SCRAPER - PINCODE VERIFICATION")
print("="*70)
print()

# Test 1: Snacks in pincode 110001 (Delhi)
print("TEST 1: Snacks in Delhi (110001)")
print("-" * 70)
response = requests.post(
    "http://localhost:8000/test-scraper",
    json={
        "category": "snacks",
        "pincode": "110001",
        "max_products": 5
    },
    timeout=300
)

if response.status_code == 200:
    data = response.json()
    print(f"✅ Status: Success")
    print(f"📍 Pincode: {data['pincode']}")
    print(f"📦 Total Products: {data['total_products']}")
    print(f"\nFirst 3 products:")
    for i, product in enumerate(data['products'][:3], 1):
        print(f"  {i}. {product['name']}")
        print(f"     Price: ₹{product['price']} | Weight: {product['weight']}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)

print()
print("="*70)
print("\n⚠️ IMPORTANT: Check the backend terminal for detailed logs including:")
print("  - Pincode verification status")
print("  - Page content analysis")
print("  - First 5 products with details")
print("="*70)
