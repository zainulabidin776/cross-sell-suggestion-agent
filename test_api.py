"""
Quick API test for recommendation endpoint
"""
import requests
import json
import time

print("Waiting for server...")
time.sleep(2)

print("\nTesting /api/recommend with valid product ID...")
try:
    response = requests.post(
        'http://localhost:5000/api/recommend',
        json={
            'product_id': 'fakestore_1',
            'limit': 4,
            'session_id': 'test_123'
        },
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    
except requests.exceptions.ConnectionError:
    print("ERROR: Server not running on http://localhost:5000")
except Exception as e:
    print(f"ERROR: {e}")
