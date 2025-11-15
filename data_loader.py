"""
Data loader to fetch products from Fake Store API and cache them.
Fetches from https://fakestoreapi.com/products and stores in PostgreSQL (or in-memory).
"""

import requests
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FAKE_STORE_API = "https://fakestoreapi.com/products"

def load_from_api():
    """Fetch products from Fake Store API"""
    try:
        logger.info(f"Fetching products from {FAKE_STORE_API}...")
        response = requests.get(FAKE_STORE_API, timeout=10)
        response.raise_for_status()
        products = response.json()
        logger.info(f"Fetched {len(products)} products")
        return products
    except Exception as e:
        logger.error(f"Failed to fetch from API: {e}")
        return None

def map_fake_store_to_cssa(products):
    """
    Transform Fake Store products into CSSA product format.
    Fake Store has: id, title, price, category, description, image, rating
    CSSA needs: id, name, category, price, cross_sell
    """
    mapped = {}
    
    if not products:
        return mapped
    
    for p in products:
        product_id = f"prod_{p['id']}"  # e.g., prod_1, prod_2
        mapped[product_id] = {
            "id": p['id'],
            "name": p['title'],
            "category": p['category'],
            "price": p['price'],
            "description": p.get('description', '')[:100],  # Truncate for brevity
            "image": p.get('image', ''),
            "rating": p.get('rating', {}).get('rate', 0),
            "cross_sell": []  # Will be populated by recommendation logic
        }
    
    # Simple cross-sell logic: suggest products from same category
    for pid, product in mapped.items():
        cross_sell = [
            other_pid for other_pid, other in mapped.items()
            if other['category'] == product['category'] and other_pid != pid
        ][:3]  # Max 3 cross-sells
        product['cross_sell'] = cross_sell
    
    return mapped

def load_from_file(filepath='products.json'):
    """Load products from local JSON file"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                logger.info(f"Loaded products from {filepath}")
                return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load from file: {e}")
    return None

def save_to_file(products, filepath='products.json'):
    """Save products to local JSON file"""
    try:
        with open(filepath, 'w') as f:
            json.dump(products, f, indent=2)
        logger.info(f"Saved {len(products)} products to {filepath}")
    except Exception as e:
        logger.error(f"Failed to save to file: {e}")

def load_and_cache():
    """Main function: fetch from API or file, cache locally"""
    # Try API first
    api_products = load_from_api()
    
    if api_products:
        mapped = map_fake_store_to_cssa(api_products)
        save_to_file(mapped, 'products.json')
        logger.info("✓ Loaded products from API and cached locally")
        return mapped
    
    # Fallback to local file
    logger.warning("API fetch failed, falling back to local cache...")
    cached = load_from_file('products.json')
    if cached:
        logger.info("✓ Loaded products from local cache")
        return cached
    
    logger.error("✗ No products available (API down and no cache)")
    return {}

if __name__ == "__main__":
    products = load_and_cache()
    print(f"\nLoaded {len(products)} products:")
    for pid, p in list(products.items())[:3]:
        print(f"  {pid}: {p['name']} (${p['price']}) - Category: {p['category']}")
    if len(products) > 3:
        print(f"  ... and {len(products) - 3} more")
