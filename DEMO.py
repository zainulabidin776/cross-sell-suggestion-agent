#!/usr/bin/env python
"""
Demonstration: How the Recommendation Engine Works with Real Data

This script shows the complete flow from API to recommendations.
"""

import json
import os

def demo():
    print("="*70)
    print("  CSSA Recommendation Engine - How It Works")
    print("="*70)
    
    # Step 1: Load products
    print("\n[1] LOADING PRODUCT DATA")
    print("-" * 70)
    
    products_file = 'products.json'
    if os.path.exists(products_file):
        with open(products_file, 'r') as f:
            products = json.load(f)
        print(f"✓ Loaded {len(products)} products from {products_file}")
        print("  (These were fetched from Fake Store API)")
    else:
        print("✗ products.json not found!")
        print("  Run: python setup.py")
        return
    
    # Step 2: Show sample products
    print("\n[2] SAMPLE PRODUCTS FROM API")
    print("-" * 70)
    product_list = list(products.items())[:5]
    for prod_id, prod in product_list:
        print(f"\n  ID: {prod_id}")
        print(f"  Name: {prod['name']}")
        print(f"  Price: ${prod['price']:.2f}")
        print(f"  Category: {prod['category']}")
        if prod.get('cross_sell'):
            print(f"  Cross-Sell: {prod['cross_sell'][:2]}...")
    
    if len(products) > 5:
        print(f"\n  ... and {len(products) - 5} more products")
    
    # Step 3: Show recommendation logic
    print("\n[3] RECOMMENDATION LOGIC")
    print("-" * 70)
    print("""
    The RecommendationEngine works like this:
    
    1. User requests: POST /api/recommend {"product_id": "prod_5"}
    2. Engine looks up "prod_5" in products catalog
    3. Gets cross_sell list (e.g., ["prod_1", "prod_3", "prod_7"])
    4. Fetches details for each cross-sell product
    5. Computes confidence score (0.0-1.0) based on category match
    6. Returns recommendations sorted by confidence
    
    Example:
    --------
    Input: {"product_id": "prod_5"}
    
    1. Found product: Books category
    2. Cross-sell products: [prod_1, prod_3, prod_7]
    3. Fetching details...
    4. All in Books category → confidence 0.8
    5. Return top 3 with details
    """)
    
    # Step 4: Simulate a recommendation
    print("\n[4] SIMULATING A RECOMMENDATION REQUEST")
    print("-" * 70)
    
    # Pick first product
    demo_prod_id, demo_prod = product_list[0]
    print(f"\nRequest: Get recommendations for '{demo_prod['name']}'")
    print(f"Product ID: {demo_prod_id}")
    print(f"Category: {demo_prod['category']}")
    
    if demo_prod.get('cross_sell'):
        print(f"\nCross-sell candidates: {demo_prod['cross_sell']}")
        print("\nRecommendations generated:")
        
        for i, cross_id in enumerate(demo_prod['cross_sell'][:3], 1):
            if cross_id in products:
                cross_prod = products[cross_id]
                confidence = 0.85 if cross_prod['category'] == demo_prod['category'] else 0.65
                print(f"\n  {i}. {cross_prod['name']}")
                print(f"     Price: ${cross_prod['price']:.2f}")
                print(f"     Category: {cross_prod['category']}")
                print(f"     Confidence: {confidence:.2f}")
                print(f"     Reason: 'Frequently bought with {demo_prod['name']}'")
    else:
        print("\n  (No cross-sell data for this product)")
    
    # Step 5: Show memory persistence
    print("\n[5] MEMORY PERSISTENCE")
    print("-" * 70)
    print("""
    After each request:
    
    Short-Term Memory (STM):
    ├─ Stored in RAM
    ├─ Session: user_session_123
    └─ Request: {"product_id": "prod_5", "recommendations": [...]}
    
    Long-Term Memory (LTM):
    ├─ Persisted to SQLite (cssa_memory.db)
    ├─ Tables: sessions, interactions
    └─ Query: SELECT * FROM interactions WHERE session_id = 'user_session_123'
    """)
    
    # Step 6: Show API examples
    print("\n[6] LIVE API EXAMPLES")
    print("-" * 70)
    print("""
    Once the agent is running (python cssa_agent.py):
    
    1. Get recommendations:
       curl -X POST http://127.0.0.1:5000/api/recommend \\
         -H "Content-Type: application/json" \\
         -d '{"product_id": "prod_1", "limit": 3}'
    
    2. Search products:
       curl -X POST http://127.0.0.1:5000/api/search \\
         -H "Content-Type: application/json" \\
         -d '{"query": "electronics"}'
    
    3. Check session memory:
       curl http://127.0.0.1:5000/api/memory
    
    4. Fetch session history:
       curl http://127.0.0.1:5000/api/memory/user_session_123
    
    5. View API docs:
       Open http://127.0.0.1:5000/ui/swagger.html
    """)
    
    # Step 7: Architecture summary
    print("\n[7] COMPLETE DATA FLOW")
    print("-" * 70)
    print("""
    ┌─────────────────────────────────────────────────────────┐
    │  Fake Store API (External, Real Products)               │
    └──────────────────────┬──────────────────────────────────┘
                           │ (fetch once via setup.py)
    ┌──────────────────────▼──────────────────────────────────┐
    │  products.json (Cached, Portable)                       │
    └──────────────────────┬──────────────────────────────────┘
                           │ (load on startup)
    ┌──────────────────────▼──────────────────────────────────┐
    │  ProductDatabase (In-Memory)                            │
    │  - Fast lookup                                          │
    │  - Cross-sell relationships                             │
    └──────────────────────┬──────────────────────────────────┘
                           │
    ┌──────────────────────▼──────────────────────────────────┐
    │  RecommendationEngine                                   │
    │  - Generate suggestions                                 │
    │  - Compute confidence scores                            │
    │  - Sort by relevance                                    │
    └──────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
    ┌─────────▼──────────┐   ┌────────▼──────────┐
    │  STM (RAM)         │   │  LTM (SQLite DB)  │
    │  - Session buffer  │   │  - Persistent     │
    │  - Fast access     │   │  - Audit trail    │
    └────────────────────┘   └───────────────────┘
                           │
    ┌──────────────────────▼──────────────────────────────────┐
    │  User / Supervisor / Tests                              │
    │  - Web UI (http://127.0.0.1:5000/)                      │
    │  - REST API (/api/recommend, /api/search, etc.)        │
    │  - Swagger Docs (http://127.0.0.1:5000/ui/swagger.html)│
    └─────────────────────────────────────────────────────────┘
    """)
    
    print("\n[✓] DEMO COMPLETE")
    print("="*70)
    print("\nNext steps:")
    print("1. python setup.py  # Load real products")
    print("2. python cssa_agent.py  # Start the agent")
    print("3. Visit http://127.0.0.1:5000/  # Try the UI")
    print("4. python test_agent.py  # Run tests")
    print("\n")

if __name__ == "__main__":
    demo()
