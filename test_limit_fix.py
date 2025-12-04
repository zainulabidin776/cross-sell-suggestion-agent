"""
Test script to verify the limit parameter works correctly
Run this AFTER starting the agent with: python cssa_agent.py
"""
import json

# Load products to test with
with open('products.json', 'r') as f:
    products = json.load(f)

print("=" * 70)
print("LIMIT FIX VERIFICATION TEST")
print("=" * 70)

# Show cross-sell availability
print("\nStep 1: Verify products have sufficient cross-sells")
print("-" * 70)
for i, (pid, product) in enumerate(list(products.items())[:5]):
    name = product['name'][:45]
    count = len(product['cross_sell'])
    status = "✓ OK" if count >= 4 else "✗ Limited"
    print(f"{i+1}. {name}... | Cross-sells: {count:2} {status}")

print("\n" + "=" * 70)
print("Step 2: Test the recommendation engine directly")
print("-" * 70)

# Import and test the recommendation engine
from cssa_agent import rec_engine, product_db

test_product_id = list(products.keys())[0]
test_product = products[test_product_id]

print(f"\nTesting with product: {test_product['name'][:50]}")
print(f"Product ID: {test_product_id}")
print(f"Category: {test_product['category']}")

# Test with different limits
for limit in [3, 4, 5, 6]:
    recs = rec_engine.generate_recommendations(test_product_id, limit=limit)
    status = "✓ PASS" if len(recs) == limit else "✗ FAIL"
    print(f"\n  Limit={limit}: Requested {limit}, Got {len(recs)} {status}")
    for j, rec in enumerate(recs, 1):
        print(f"    {j}. {rec['name'][:40]}... (score: {rec['confidence_score']})")

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
print("\nIf all tests show ✓ PASS, the limit fix is working correctly!")
print("\nTo test via API:")
print("  1. Run: python cssa_agent.py")
print("  2. Open: http://127.0.0.1:5000/")
print("  3. Search for a product and try different limit values")
