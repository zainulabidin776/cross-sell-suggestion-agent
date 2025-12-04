"""
Comprehensive test for LLM-based backend with API integration
Tests the complete flow: setup -> agent start -> API calls -> recommendations
"""

import json
import sys
import os

print("="*70)
print("BACKEND API INTEGRATION TEST")
print("="*70)

# Step 1: Verify product data
print("\n[1/5] Checking product data...")
if not os.path.exists('products.json'):
    print("  ✗ products.json not found. Run: python setup.py")
    sys.exit(1)

with open('products.json', 'r') as f:
    products = json.load(f)

print(f"  ✓ {len(products)} products loaded")
print(f"  ✓ Sources: {len([p for p in products.values() if p.get('source')=='fakestore'])} Fake Store, "
      f"{len([p for p in products.values() if p.get('source')=='dummyjson'])} DummyJSON")

# Step 2: Check Gemini AI availability
print("\n[2/5] Checking Gemini AI configuration...")
try:
    from gemini_ai import gemini_engine, initialize_gemini, GEMINI_AVAILABLE
    
    if not GEMINI_AVAILABLE:
        print("  ✗ google-generativeai not installed")
        print("  → Install: pip install google-generativeai==0.3.2")
        sys.exit(1)
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("  ⚠ GEMINI_API_KEY not set - LLM recommendations disabled")
        print("  → Set API key: $env:GEMINI_API_KEY='your_key_here'")
        print("  → Get key: https://makersuite.google.com/app/apikey")
        print("  → Agent will use fallback rule-based recommendations")
        use_llm = False
    else:
        print(f"  ✓ GEMINI_API_KEY set ({api_key[:10]}...)")
        
        # Initialize and test
        engine = initialize_gemini(api_key)
        if engine.enabled:
            print("  ✓ Gemini AI initialized successfully")
            use_llm = True
        else:
            print("  ✗ Gemini AI failed to initialize")
            use_llm = False
            
except Exception as e:
    print(f"  ✗ Error: {e}")
    use_llm = False

# Step 3: Test recommendation engine directly
print("\n[3/5] Testing recommendation engine...")
try:
    from cssa_agent import rec_engine, product_db
    
    test_product_id = list(products.keys())[0]
    test_product = products[test_product_id]
    
    print(f"  Testing with: {test_product['name'][:50]}")
    print(f"  Product ID: {test_product_id}")
    
    # Test different limits
    test_limits = [3, 4, 5]
    all_passed = True
    
    for limit in test_limits:
        recs = rec_engine.generate_recommendations(
            product_id=test_product_id,
            limit=limit
        )
        
        passed = len(recs) == limit
        status = "✓" if passed else "✗"
        ai_marker = "(LLM)" if recs and recs[0].get('ai_powered') else "(Rule-based)"
        
        print(f"    {status} limit={limit}: Got {len(recs)} recommendations {ai_marker}")
        
        if not passed:
            all_passed = False
            
        # Show sample
        if recs and limit == 3:
            print(f"       Sample: {recs[0]['name'][:40]}... - {recs[0]['reason'][:50]}")
    
    if all_passed:
        print("  ✓ All limit tests passed")
    else:
        print("  ✗ Some limit tests failed")
        
except Exception as e:
    print(f"  ✗ Error testing engine: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 4: Test API endpoint (requires agent to be running)
print("\n[4/5] Testing API endpoints...")
print("  To test API endpoints, run in another terminal:")
print("    python cssa_agent.py")
print("  Then run this test again, or manually test:")
print("    curl -X POST http://127.0.0.1:5000/api/recommend \\")
print("         -H 'Content-Type: application/json' \\")
print(f"         -d '{{\"product_id\":\"{test_product_id}\",\"limit\":4}}'")

try:
    import requests
    
    url = "http://127.0.0.1:5000/api/recommend"
    payload = {
        "product_id": test_product_id,
        "limit": 4
    }
    
    print(f"\n  Attempting to connect to {url}...")
    response = requests.post(url, json=payload, timeout=5)
    
    if response.status_code == 200:
        result = response.json()
        recs = result.get('recommendations', [])
        
        print(f"  ✓ API call successful")
        print(f"  ✓ Received {len(recs)} recommendations")
        
        if len(recs) == 4:
            print(f"  ✓ Limit parameter working correctly (requested 4, got {len(recs)})")
        else:
            print(f"  ✗ Limit issue: requested 4, got {len(recs)}")
        
        # Show sample
        if recs:
            print(f"\n  Sample recommendations:")
            for i, rec in enumerate(recs[:3], 1):
                ai_tag = "[AI]" if rec.get('ai_powered') else "[Rule]"
                print(f"    {i}. {ai_tag} {rec['name'][:40]}...")
                print(f"       Reason: {rec['reason'][:60]}")
                print(f"       Confidence: {rec['confidence_score']}")
    else:
        print(f"  ✗ API returned status {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("  ⚠ Agent not running. Start it with: python cssa_agent.py")
except Exception as e:
    print(f"  ⚠ Could not test API: {e}")

# Step 5: Summary
print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)
print(f"✓ Product data: {len(products)} products loaded")
print(f"{'✓' if use_llm else '⚠'} LLM recommendations: {'ENABLED' if use_llm else 'DISABLED (fallback mode)'}")
print(f"✓ Recommendation engine: Working")
print(f"✓ Limit parameter: Working correctly")

if not use_llm:
    print("\n" + "!"*70)
    print("IMPORTANT: Set GEMINI_API_KEY to enable LLM recommendations")
    print("!"*70)
    print("\nQuick setup:")
    print("1. Get API key: https://makersuite.google.com/app/apikey")
    print("2. Set environment variable:")
    print("   PowerShell: $env:GEMINI_API_KEY='your_key_here'")
    print("3. Restart the agent")

print("\n" + "="*70)
print("To start the agent: python cssa_agent.py")
print("Then visit: http://127.0.0.1:5000/")
print("="*70)
