#!/usr/bin/env python3
"""Quick test to check if the server is running and auth routes are accessible."""

import requests
import sys

BASE_URL = "http://localhost:8000"

def test_server():
    """Test if server is running and routes are accessible."""
    print("Testing server connection...")
    
    # Test health endpoint
    try:
        print(f"\n1. Testing health endpoint: {BASE_URL}/api/health")
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error: {response.text}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Server is not running or not accessible on port 8000")
        print("   Please start the server with: python start_ui.py")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test auth signup endpoint (should return 400 for missing data, not timeout)
    try:
        print(f"\n2. Testing auth signup endpoint: {BASE_URL}/api/auth/signup")
        response = requests.post(
            f"{BASE_URL}/api/auth/signup",
            json={},
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        # Any response (even 400/422) means the route is registered
        if response.status_code in [400, 422, 201]:
            print("   ✅ Route is accessible")
        else:
            print(f"   ⚠️  Unexpected status code")
    except requests.exceptions.Timeout:
        print("   ❌ Request timed out - route may not be registered")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test auth login endpoint
    try:
        print(f"\n3. Testing auth login endpoint: {BASE_URL}/api/auth/login")
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "test@test.com", "password": "test"},
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        # 401 is expected for invalid credentials, means route works
        if response.status_code in [401, 200]:
            print("   ✅ Route is accessible")
        else:
            print(f"   ⚠️  Unexpected status code")
    except requests.exceptions.Timeout:
        print("   ❌ Request timed out - route may not be registered")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print("\n✅ Server is running and routes are accessible!")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1]
    success = test_server()
    sys.exit(0 if success else 1)

