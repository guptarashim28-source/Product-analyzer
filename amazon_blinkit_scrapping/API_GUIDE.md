# API Reference Guide

Complete API documentation for the Blinkit Product Insights Platform.

## Base URL

```
http://localhost:8000
```

## Endpoints

### 1. Health Check

Check if the API is running.

**Endpoint:** `GET /api/health`

**Request:**
```bash
curl http://localhost:8000/api/health
```

**Response:**
```json
{
  "status": "ok"
}
```

**Status Codes:**
- `200 OK` - Service is healthy

---

### 2. Scrape Products

Scrape products from Blinkit for multiple pincodes and a search query.

**Endpoint:** `POST /api/scrape`

**Request Body:**
```json
{
  "pincodes": ["110001", "560001"],
  "query": "protein bar",
  "save_html": false,
  "max_scrolls": 40
}
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `pincodes` | `string[]` | Yes | - | List of Indian pincodes to scrape |
| `query` | `string` | Yes | - | Product search query (e.g., "milk", "snacks") |
| `save_html` | `boolean` | No | `false` | Save raw HTML pages to disk for debugging |
| `max_scrolls` | `integer` | No | `40` | Maximum scroll attempts to load products |

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "pincodes": ["110001", "560001"],
    "query": "protein bar",
    "save_html": false,
    "max_scrolls": 40
  }'
```

**Response:**
```json
{
  "summary": {
    "pincodes": ["110001", "560001"],
    "query": "protein bar",
    "total_products": 45
  },
  "brand_top10_counts": [
    {
      "brand": "MuscleBlaze",
      "count": 8
    },
    {
      "brand": "Yoga",
      "count": 6
    },
    {
      "brand": "RiteBite",
      "count": 4
    }
  ],
  "products": [
    {
      "pincode": "110001",
      "rank": 1,
      "brand": "MuscleBlaze",
      "name": "MuscleBlaze High Protein Bar - Chocolate",
      "weight": "100 g",
      "price": 150.0,
      "price_text": "₹150",
      "grams": 100.0,
      "price_per_100g": 150.0
    },
    {
      "pincode": "110001",
      "rank": 2,
      "brand": "Yoga",
      "name": "Yoga Protein Bar - Peanut Butter",
      "weight": "50 g",
      "price": 80.0,
      "price_text": "₹80",
      "grams": 50.0,
      "price_per_100g": 160.0
    }
  ]
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `summary` | `object` | Aggregated statistics |
| `summary.pincodes` | `string[]` | Pincodes that were scraped |
| `summary.query` | `string` | Search query used |
| `summary.total_products` | `integer` | Total products across all pincodes |
| `brand_top10_counts` | `object[]` | Brands ranked by top-10 appearances |
| `brand_top10_counts[].brand` | `string` | Brand name |
| `brand_top10_counts[].count` | `integer` | Times appeared in top 10 across pincodes |
| `products` | `object[]` | Full product list |
| `products[].pincode` | `string` | Location pincode |
| `products[].rank` | `integer` | Position in search results (1-based) |
| `products[].brand` | `string` | Extracted brand name |
| `products[].name` | `string` | Full product name |
| `products[].weight` | `string` | Original weight text |
| `products[].price` | `float \| null` | Price in rupees |
| `products[].price_text` | `string` | Original price text from page |
| `products[].grams` | `float \| null` | Weight in grams (parsed) |
| `products[].price_per_100g` | `float \| null` | Normalized price per 100g |

**Status Codes:**
- `200 OK` - Success
- `422 Unprocessable Entity` - Invalid request parameters
- `500 Internal Server Error` - Scraping or parsing error

**Example with Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/scrape",
    json={
        "pincodes": ["110001"],
        "query": "milk",
        "save_html": False
    }
)

data = response.json()
print(f"Found {data['summary']['total_products']} products")

for product in data['products'][:5]:
    print(f"{product['name']} - ₹{product['price_per_100g']}/100g")
```

---

### 3. Export to CSV

Same as scrape endpoint but returns CSV file for download.

**Endpoint:** `POST /api/export-csv`

**Request Body:** (Same as `/api/scrape`)
```json
{
  "pincodes": ["110001"],
  "query": "snacks",
  "save_html": false,
  "max_scrolls": 40
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/export-csv \
  -H "Content-Type: application/json" \
  -d '{
    "pincodes": ["110001", "560001"],
    "query": "protein bar"
  }' \
  --output blinkit_products.csv
```

**Response:** CSV file with headers:
```
pincode,rank,brand,name,weight,price,price_text,grams,price_per_100g
110001,1,MuscleBlaze,MuscleBlaze High Protein Bar,100 g,150.0,₹150,100.0,150.0
110001,2,Yoga,Yoga Protein Bar,50 g,80.0,₹80,50.0,160.0
```

**Response Headers:**
```
Content-Type: text/csv
Content-Disposition: attachment; filename=blinkit_products_110001_560001_protein_bar.csv
```

**Status Codes:**
- `200 OK` - CSV file returned
- `422 Unprocessable Entity` - Invalid parameters
- `500 Internal Server Error` - Scraping error

**Example with Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/export-csv",
    json={"pincodes": ["110001"], "query": "milk"}
)

with open("output.csv", "wb") as f:
    f.write(response.content)

print("CSV saved to output.csv")
```

---

## Common Use Cases

### 1. Compare Prices Across Cities

```bash
curl -X POST http://localhost:8000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "pincodes": ["110001", "400001", "560001", "700001"],
    "query": "milk"
  }'
```

### 2. Track Brand Visibility

```python
import requests

response = requests.post(
    "http://localhost:8000/api/scrape",
    json={"pincodes": ["110001"], "query": "protein bar"}
).json()

print("Top brands in search results:")
for brand in response['brand_top10_counts']:
    print(f"{brand['brand']}: {brand['count']} times in top 10")
```

### 3. Find Best Value Products

```python
import requests

response = requests.post(
    "http://localhost:8000/api/scrape",
    json={"pincodes": ["110001"], "query": "chocolate"}
).json()

# Sort by price per 100g
products = [p for p in response['products'] if p['price_per_100g']]
products.sort(key=lambda x: x['price_per_100g'])

print("Best value chocolates:")
for p in products[:5]:
    print(f"{p['name']} - ₹{p['price_per_100g']}/100g")
```

### 4. Batch Export for Multiple Queries

```bash
# Save results for different product categories
for query in "milk" "bread" "eggs" "butter"; do
  curl -X POST http://localhost:8000/api/export-csv \
    -H "Content-Type: application/json" \
    -d "{\"pincodes\": [\"110001\"], \"query\": \"$query\"}" \
    --output "${query}_products.csv"
done
```

---

## Error Handling

### Common Errors

**Invalid Pincode:**
```json
{
  "detail": [
    {
      "loc": ["body", "pincodes", 0],
      "msg": "string does not match regex",
      "type": "value_error.str.regex"
    }
  ]
}
```

**Empty Products:**
```json
{
  "summary": {
    "pincodes": ["999999"],
    "query": "test",
    "total_products": 0
  },
  "brand_top10_counts": [],
  "products": []
}
```

**Server Error:**
```json
{
  "detail": "Internal server error"
}
```

### Retry Logic

```python
import requests
import time

def scrape_with_retry(pincodes, query, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(
                "http://localhost:8000/api/scrape",
                json={"pincodes": pincodes, "query": query},
                timeout=120  # 2 minutes
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait = 2 ** attempt  # Exponential backoff
                print(f"Error: {e}. Retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise

# Usage
data = scrape_with_retry(["110001"], "milk")
```

---

## Rate Limiting

**Current:** No rate limiting implemented

**Recommendations:**
- Wait ~60 seconds between requests for the same pincode
- Limit to 5-10 pincodes per request
- Don't exceed 100 products per query (adjust `max_scrolls`)

---

## Performance Tips

1. **Reduce Scroll Count:**
   ```json
   {"max_scrolls": 20}  // Faster, fewer products
   ```

2. **Use Specific Queries:**
   ```json
   {"query": "amul milk"}  // Better than just "milk"
   ```

3. **Batch Pincodes:**
   ```json
   {"pincodes": ["110001", "110002", "110003"]}  // One request
   ```

4. **Avoid Saving HTML:**
   ```json
   {"save_html": false}  // Faster response
   ```

---

## Testing

### Using cURL

```bash
# Health check
curl http://localhost:8000/api/health

# Scrape (pretty print with jq)
curl -X POST http://localhost:8000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"pincodes":["110001"],"query":"milk"}' \
  | jq .

# Export CSV
curl -X POST http://localhost:8000/api/export-csv \
  -H "Content-Type: application/json" \
  -d '{"pincodes":["110001"],"query":"milk"}' \
  -o test.csv
```

### Using Postman

1. **Import Collection:**
   - Method: `POST`
   - URL: `http://localhost:8000/api/scrape`
   - Headers: `Content-Type: application/json`
   - Body (raw JSON):
     ```json
     {
       "pincodes": ["110001"],
       "query": "milk"
     }
     ```

2. **Run Request**
3. **View Response**

---

## OpenAPI / Swagger Docs

Interactive API documentation available at:

```
http://localhost:8000/docs
```

Features:
- Try endpoints directly from browser
- See request/response schemas
- Download OpenAPI spec

---

## Support

For API issues:
- Check server logs in terminal
- Enable debug mode: `export BLINKIT_HEADLESS=0`
- Open issue: [GitHub Issues](https://github.com/anubhav-77-dev/blinkit/issues)

---

**Happy scraping! 🚀**
