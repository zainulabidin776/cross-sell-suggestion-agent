"""
Test script for Cross-Sell Suggestion Agent
Tests various product types with different limits
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_recommendation(product_id, limit=3):
    """Test recommendation endpoint"""
    print(f"\n{'='*70}")
    print(f"Testing: {product_id} (limit={limit})")
    print('='*70)
    
    payload = {
        "product_id": product_id,
        "limit": limit,
        "session_id": "test_session"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/recommend", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data['status']}")
            print(f"Model: {data['model']}")
            print(f"Recommendations ({len(data['recommendations'])}):\n")
            
            for i, rec in enumerate(data['recommendations'], 1):
                print(f"{i}. {rec['product_name']}")
                print(f"   Category: {rec['category']}")
                print(f"   Price: {rec['estimated_price']}")
                print(f"   Reason: {rec['reason']}")
                print()
            
            return True
        else:
            print(f"Error: {response.status_code}")
            print(response.json())
            return False
            
    except Exception as e:
        print(f"Exception: {e}")
        return False

def test_status():
    """Test status endpoint"""
    print(f"\n{'='*70}")
    print("Testing: Agent Status")
    print('='*70)
    
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        data = response.json()
        print(json.dumps(data, indent=2))
        return True
    except Exception as e:
        print(f"Exception: {e}")
        return False

if __name__ == '__main__':
    print("\n" + "="*70)
    print("Cross-Sell Suggestion Agent - Test Suite")
    print("="*70)
    
    # Test status first
    test_status()
    
    # Test different products
    test_products = [
        ("laptop", 3),
        ("mouse", 5),
        ("smartphone", 4),
        ("camera", 2),
        ("headphones", 3)
    ]
    
    for product, limit in test_products:
        test_recommendation(product, limit)
    
    # Test edge cases
    print(f"\n{'='*70}")
    print("Testing Edge Cases")
    print('='*70)
    
    print("\nTest 1: Limit = 0 (should return empty)")
    test_recommendation("laptop", 0)
    
    print("\nTest 2: Limit > 5 (should cap at 5)")
    test_recommendation("tablet", 10)
    
    print("\n" + "="*70)
    print("Test Suite Complete!")
    print("="*70)
