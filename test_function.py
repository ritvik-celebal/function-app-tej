#!/usr/bin/env python3
"""
Test script for Azure Function App
This script tests the deployed function endpoints
"""

import requests
import json
import sys
import time
from typing import Dict, Any

def test_http_function(base_url: str) -> bool:
    """Test the HTTP trigger function"""
    endpoint = f"{base_url}/api/HttpTriggerFunction"
    
    print(f"Testing HTTP function: {endpoint}")
    
    try:
        response = requests.get(endpoint, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Response:")
            print(json.dumps(result, indent=2))
            
            # Check required fields
            required_fields = ["message", "status", "managed_identity"]
            for field in required_fields:
                if field not in result:
                    print(f"❌ Missing required field: {field}")
                    return False
            
            if result.get("status") == "success":
                print("✅ HTTP function test passed!")
                return True
            else:
                print("❌ Function returned error status")
                return False
                
        else:
            print(f"❌ HTTP function failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_function_health(base_url: str) -> bool:
    """Test function app health"""
    endpoint = f"{base_url}/admin/host/status"
    
    print(f"Testing function health: {endpoint}")
    
    try:
        response = requests.get(endpoint, timeout=10)
        print(f"Health Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Function app is healthy!")
            return True
        else:
            print(f"⚠️ Health check returned status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Health check failed: {e}")
        return False

def main():
    """Main test function"""
    if len(sys.argv) != 2:
        print("Usage: python test_function.py <function-app-url>")
        print("Example: python test_function.py https://my-function-app.azurewebsites.net")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    print(f"🧪 Testing Azure Function App: {base_url}")
    print("=" * 50)
    
    # Test health first
    health_ok = test_function_health(base_url)
    
    print()
    
    # Test HTTP function
    http_ok = test_http_function(base_url)
    
    print()
    print("=" * 50)
    
    if http_ok:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
