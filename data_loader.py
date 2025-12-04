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

# Multiple API sources for more products
FAKE_STORE_API = "https://fakestoreapi.com/products"
DUMMY_JSON_API = "https://dummyjson.com/products"

def load_from_api():
    """Fetch products from Fake Store API"""
    try:
        logger.info(f"Fetching products from {FAKE_STORE_API}...")
        response = requests.get(FAKE_STORE_API, timeout=10)
        response.raise_for_status()
        products = response.json()
        logger.info(f"Fetched {len(products)} products from Fake Store API")
        return products
    except Exception as e:
        logger.error(f"Failed to fetch from Fake Store API: {e}")
        return None

def load_from_dummyjson():
    """Fetch additional products from DummyJSON API"""
    try:
        logger.info(f"Fetching products from {DUMMY_JSON_API}?limit=50...")
        response = requests.get(f"{DUMMY_JSON_API}?limit=50", timeout=10)
        response.raise_for_status()
        data = response.json()
        products = data.get('products', [])
        logger.info(f"Fetched {len(products)} products from DummyJSON API")
        return products
    except Exception as e:
        logger.error(f"Failed to fetch from DummyJSON: {e}")
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
        product_id = f"fakestore_{p['id']}"  # e.g., fakestore_1, fakestore_2
        mapped[product_id] = {
            "id": p['id'],
            "name": p['title'],
            "category": p['category'],
            "price": p['price'],
            "description": p.get('description', '')[:150],  # Increased for better context
            "image": p.get('image', ''),
            "rating": p.get('rating', {}).get('rate', 0),
            "source": "fakestore",
            "cross_sell": []  # Will be populated by recommendation logic
        }
    
    return mapped

def map_dummyjson_to_cssa(products):
    """
    Transform DummyJSON products into CSSA product format.
    DummyJSON has: id, title, price, category, description, images, rating
    """
    mapped = {}
    
    if not products:
        return mapped
    
    for p in products:
        product_id = f"dummyjson_{p['id']}"
        mapped[product_id] = {
            "id": p['id'],
            "name": p.get('title', p.get('name', 'Unknown Product')),
            "category": p.get('category', 'general'),
            "price": p.get('price', 0),
            "description": p.get('description', '')[:150],
            "image": p.get('thumbnail', p.get('images', [''])[0] if p.get('images') else ''),
            "rating": p.get('rating', 0),
            "source": "dummyjson",
            "cross_sell": []
        }
    
    return mapped

def generate_cross_sell_mappings(all_products):
    """Generate intelligent cross-sell mappings for all products"""
    # Enhanced cross-sell logic with more category relationships
    category_map = {
        "men's clothing": ["women's clothing", "jewelery", "accessories"],
        "women's clothing": ["men's clothing", "jewelery", "accessories"],
        "electronics": ["accessories", "laptops", "smartphones"],
        "jewelery": ["men's clothing", "women's clothing", "accessories"],
        "accessories": ["electronics", "men's clothing", "women's clothing"],
        "laptops": ["electronics", "accessories"],
        "smartphones": ["electronics", "accessories"],
        "furniture": ["home-decoration", "lighting"],
        "home-decoration": ["furniture", "lighting"],
        "fragrances": ["beauty", "skincare"],
        "beauty": ["fragrances", "skincare"],
        "skincare": ["beauty", "fragrances"],
        "groceries": ["fragrances"],
        "general": []  # Will match any category
    }
    
    for pid, product in all_products.items():
        cat = product['category'].lower()
        
        # First: same category products (prioritize same category)
        same_cat = [
            other_pid for other_pid, other in all_products.items()
            if other['category'].lower() == cat and other_pid != pid
        ]
        
        # Second: related category products
        related_cats = category_map.get(cat, [])
        related = [
            other_pid for other_pid, other in all_products.items()
            if other['category'].lower() in related_cats and other_pid != pid
        ]
        
        # Third: if we don't have enough, add some random products
        if len(same_cat) + len(related) < 10:
            other_prods = [
                other_pid for other_pid in all_products.keys()
                if other_pid != pid and other_pid not in same_cat and other_pid not in related
            ]
            # Combine: same category first, then related, then others, up to 15 total
            cross_sell = (same_cat + related + other_prods)[:15]
        else:
            cross_sell = (same_cat + related)[:15]
        
        product['cross_sell'] = cross_sell
    
    return all_products

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
    """Main function: fetch from multiple APIs, merge, and cache locally"""
    all_products = {}
    
    # Try Fake Store API
    fakestore_products = load_from_api()
    if fakestore_products:
        mapped_fakestore = map_fake_store_to_cssa(fakestore_products)
        all_products.update(mapped_fakestore)
        logger.info(f"✓ Added {len(mapped_fakestore)} products from Fake Store API")
    
    # Try DummyJSON API
    dummyjson_products = load_from_dummyjson()
    if dummyjson_products:
        mapped_dummyjson = map_dummyjson_to_cssa(dummyjson_products)
        all_products.update(mapped_dummyjson)
        logger.info(f"✓ Added {len(mapped_dummyjson)} products from DummyJSON API")
    
    if all_products:
        # Generate intelligent cross-sell mappings
        all_products = generate_cross_sell_mappings(all_products)
        save_to_file(all_products, 'products.json')
        logger.info(f"✓ Total {len(all_products)} products loaded and cached locally")
        return all_products
    
    # Fallback to local file
    logger.warning("All APIs failed, falling back to local cache...")
    cached = load_from_file('products.json')
    if cached:
        logger.info("✓ Loaded products from local cache")
        return cached
    
    logger.error("✗ No products available (APIs down and no cache)")
    return {}

if __name__ == "__main__":
    products = load_and_cache()
    print(f"\nLoaded {len(products)} products:")
    
    # Show category distribution
    from collections import Counter
    categories = Counter([p['category'] for p in products.values()])
    print("\nCategory distribution:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count} products")
    
    print("\nSample products:")
    for pid, p in list(products.items())[:5]:
        print(f"  {pid}: {p['name'][:50]}... (${p['price']}) - {p['category']}")
    if len(products) > 5:
        print(f"  ... and {len(products) - 5} more")
