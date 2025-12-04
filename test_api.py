"""
Quick API test for recommendation endpoint
"""
import requests
import json
import time

print("Waiting for server...")
time.sleep(2)

# Test 1: Product in catalog (laptop)
print("\n=== Test 1: Product in catalog (laptop) ===")
try:
    response = requests.post(
        'http://localhost:5000/api/recommend',
        json={
            'product_id': 'laptop',
            'limit': 3,
            'session_id': 'test_123'
        },
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    
except Exception as e:
    print(f"ERROR: {e}")

# Test 2: Product NOT in catalog (mouse)
print("\n=== Test 2: Product NOT in catalog (mouse) - AI Generation ===")
try:
    response = requests.post(
        'http://localhost:5000/api/recommend',
        json={
            'product_id': 'mouse',
            'limit': 4
        },
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Status: {result.get('status')}")
    print(f"Recommendation Type: {result.get('recommendation_type')}")
    print(f"Query Product: {result.get('query_product')}")
    print(f"\nRecommendations ({len(result.get('recommendations', []))}):")
    for i, rec in enumerate(result.get('recommendations', []), 1):
        print(f"  {i}. {rec['name']} - {rec.get('price', 'N/A')}")
        print(f"     Reason: {rec['reason']}")
        print(f"     Confidence: {rec['confidence_score']}")
    
except Exception as e:
    print(f"ERROR: {e}")

print("\n=== Tests Complete ===")

