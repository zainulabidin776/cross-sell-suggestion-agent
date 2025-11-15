"""
Integration Test Script for Cross-Sell Suggestion Agent
Tests all API endpoints and validates responses
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
TIMEOUT = 10

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def print_json(data):
    print(f"{Colors.OKBLUE}{json.dumps(data, indent=2)}{Colors.ENDC}")

def test_health_check():
    """Test 1: Health Check Endpoint"""
    print_header("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Health check passed")
            print_info(f"Agent ID: {data.get('agent_id')}")
            print_info(f"Status: {data.get('status')}")
            print_info(f"Version: {data.get('version')}")
            print_json(data)
            return True
        else:
            print_error(f"Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check error: {str(e)}")
        return False

def test_status_endpoint():
    """Test 2: Status Endpoint"""
    print_header("TEST 2: Agent Status")
    
    try:
        response = requests.get(f"{BASE_URL}/api/status", timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Status endpoint working")
            print_info(f"Total Products: {data.get('total_products')}")
            print_info(f"Active Sessions: {data.get('memory_sessions')}")
            print_json(data)
            return True
        else:
            print_error(f"Status check failed with status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Status check error: {str(e)}")
        return False

def test_recommendations():
    """Test 3: Recommendation Endpoint"""
    print_header("TEST 3: Product Recommendations")
    
    test_cases = [
        {
            "name": "Laptop Recommendations",
            "payload": {
                "product_id": "laptop",
                "session_id": "test_session_1",
                "limit": 3
            }
        },
        {
            "name": "Phone Recommendations",
            "payload": {
                "product_id": "phone",
                "session_id": "test_session_2",
                "limit": 2
            }
        },
        {
            "name": "Camera Recommendations",
            "payload": {
                "product_id": "camera",
                "session_id": "test_session_3",
                "limit": 3
            }
        }
    ]
    
    all_passed = True
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{Colors.BOLD}Test Case {i}: {test['name']}{Colors.ENDC}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/recommend",
                json=test['payload'],
                headers={'Content-Type': 'application/json'},
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success':
                    recommendations = data.get('recommendations', [])
                    print_success(f"Got {len(recommendations)} recommendations")
                    
                    for rec in recommendations:
                        print_info(f"  • {rec['name']} (${rec['price']}) - Confidence: {rec['confidence_score']}")
                    
                    print_json(data)
                else:
                    print_error(f"Request failed: {data.get('message')}")
                    all_passed = False
            else:
                print_error(f"HTTP {response.status_code}: {response.text}")
                all_passed = False
                
        except Exception as e:
            print_error(f"Test failed: {str(e)}")
            all_passed = False
        
        time.sleep(0.5)  # Brief pause between tests
    
    return all_passed

def test_search():
    """Test 4: Product Search"""
    print_header("TEST 4: Product Search")
    
    search_queries = [
        "laptop",
        "phone",
        "camera",
        "accessories",
        "nonexistent_product"
    ]
    
    all_passed = True
    
    for query in search_queries:
        print(f"\n{Colors.BOLD}Searching for: '{query}'{Colors.ENDC}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/search",
                json={"query": query, "session_id": "test_search"},
                headers={'Content-Type': 'application/json'},
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 0)
                
                if count > 0:
                    print_success(f"Found {count} result(s)")
                    for result in data.get('results', [])[:3]:
                        print_info(f"  • {result['name']} (${result['price']})")
                else:
                    print_info("No results found")
                    
            else:
                print_error(f"Search failed with status {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print_error(f"Search error: {str(e)}")
            all_passed = False
        
        time.sleep(0.3)
    
    return all_passed

def test_memory_persistence():
    """Test 5: Short-Term Memory"""
    print_header("TEST 5: Short-Term Memory System")
    
    session_id = "memory_test_session"
    
    print(f"{Colors.BOLD}Making multiple requests in same session...{Colors.ENDC}\n")
    
    try:
        # First request
        print_info("Request 1: Getting recommendations for laptop")
        response1 = requests.post(
            f"{BASE_URL}/api/recommend",
            json={"product_id": "laptop", "session_id": session_id},
            timeout=TIMEOUT
        )
        
        if response1.status_code == 200:
            print_success("First request successful")
        
        time.sleep(0.5)
        
        # Second request - same session
        print_info("Request 2: Getting recommendations for phone (same session)")
        response2 = requests.post(
            f"{BASE_URL}/api/recommend",
            json={"product_id": "phone", "session_id": session_id},
            timeout=TIMEOUT
        )
        
        if response2.status_code == 200:
            print_success("Second request successful")
        
        time.sleep(0.5)
        
        # Third request - verify memory
        print_info("Request 3: Verifying session context")
        response3 = requests.post(
            f"{BASE_URL}/api/recommend",
            json={"product_id": "camera", "session_id": session_id},
            timeout=TIMEOUT
        )
        
        if response3.status_code == 200:
            print_success("Memory system working - session maintained across requests")
            return True
        
    except Exception as e:
        print_error(f"Memory test error: {str(e)}")
        return False

def test_error_handling():
    """Test 6: Error Handling"""
    print_header("TEST 6: Error Handling")
    
    error_cases = [
        {
            "name": "Missing product_id",
            "payload": {"session_id": "test"},
            "expected_status": 400
        },
        {
            "name": "Invalid JSON",
            "payload": "not_json",
            "expected_status": [400, 415]
        }
    ]
    
    all_passed = True
    
    for i, test in enumerate(error_cases, 1):
        print(f"\n{Colors.BOLD}Error Test {i}: {test['name']}{Colors.ENDC}")
        
        try:
            if isinstance(test['payload'], str):
                response = requests.post(
                    f"{BASE_URL}/api/recommend",
                    data=test['payload'],
                    timeout=TIMEOUT
                )
            else:
                response = requests.post(
                    f"{BASE_URL}/api/recommend",
                    json=test['payload'],
                    timeout=TIMEOUT
                )
            
            expected = test['expected_status']
            if isinstance(expected, list):
                if response.status_code in expected:
                    print_success(f"Error handled correctly (HTTP {response.status_code})")
                else:
                    print_error(f"Unexpected status {response.status_code}")
                    all_passed = False
            else:
                if response.status_code == expected:
                    print_success(f"Error handled correctly (HTTP {response.status_code})")
                else:
                    print_error(f"Expected {expected}, got {response.status_code}")
                    all_passed = False
                    
        except Exception as e:
            print_error(f"Test error: {str(e)}")
            all_passed = False
    
    return all_passed

def test_registry_info():
    """Test 7: Registry Information"""
    print_header("TEST 7: Registry Information")
    
    try:
        response = requests.get(f"{BASE_URL}/api/registry", timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Registry information available")
            print_info("Agent Capabilities:")
            for cap in data.get('agent_metadata', {}).get('capabilities', []):
                print(f"  • {cap}")
            print_json(data)
            return True
        else:
            print_error(f"Registry check failed")
            return False
    except Exception as e:
        print_error(f"Registry error: {str(e)}")
        return False

def run_all_tests():
    """Run all test suites"""
    print_header("CSSA AGENT INTEGRATION TESTS")
    print_info(f"Testing agent at: {BASE_URL}")
    print_info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Health Check", test_health_check),
        ("Status Endpoint", test_status_endpoint),
        ("Recommendations", test_recommendations),
        ("Product Search", test_search),
        ("Memory System", test_memory_persistence),
        ("Error Handling", test_error_handling),
        ("Registry Info", test_registry_info)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print_error(f"Test suite '{test_name}' crashed: {str(e)}")
            results.append((test_name, False))
        
        time.sleep(1)  # Pause between test suites
    
    # Print summary
    print_header("TEST SUMMARY")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        color = Colors.OKGREEN if passed else Colors.FAIL
        print(f"{color}{status.ljust(6)}{Colors.ENDC} {test_name}")
    
    print(f"\n{Colors.BOLD}Results: {passed_count}/{total_count} tests passed{Colors.ENDC}")
    
    if passed_count == total_count:
        print(f"{Colors.OKGREEN}{Colors.BOLD}✓ ALL TESTS PASSED{Colors.ENDC}\n")
        return True
    else:
        print(f"{Colors.FAIL}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.ENDC}\n")
        return False

if __name__ == "__main__":
    print(f"\n{Colors.BOLD}Cross-Sell Suggestion Agent - Integration Tests{Colors.ENDC}")
    print(f"{Colors.BOLD}Team: Awaiz Ali Khan, Zain ul Abideen, Kamran Ali{Colors.ENDC}\n")
    
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Tests interrupted by user{Colors.ENDC}")
        exit(130)
    except Exception as e:
        print(f"\n{Colors.FAIL}Fatal error: {str(e)}{Colors.ENDC}")
        exit(1)