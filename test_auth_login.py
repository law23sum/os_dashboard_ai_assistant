#!/usr/bin/env python3
"""Test script for authentication login endpoint for both regular and admin accounts."""

import requests
import json
import sys
from typing import Dict, Any

# Default base URL - adjust if your server runs on a different port
BASE_URL = "http://localhost:8000"


def test_login(email: str, password: str, user_type: str) -> Dict[str, Any]:
    """Test login endpoint with given credentials."""
    url = f"{BASE_URL}/api/auth/login"
    
    # Try with email
    payload = {
        "email": email,
        "password": password
    }
    
    print(f"\n{'='*60}")
    print(f"Testing {user_type} login with email: {email}")
    print(f"{'='*60}")
    print(f"POST {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ SUCCESS - {user_type} login successful!")
            print(f"Access Token: {data.get('access_token', '')[:50]}...")
            print(f"User Info:")
            user_info = data.get('user', {})
            print(f"  - ID: {user_info.get('id')}")
            print(f"  - Email: {user_info.get('email')}")
            print(f"  - Display Name: {user_info.get('display_name')}")
            print(f"  - Is Admin: {user_info.get('is_admin')}")
            print(f"  - Environment: {user_info.get('environment')}")
            return {"success": True, "data": data}
        else:
            print(f"\n❌ FAILED - Status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error: {response.text}")
            return {"success": False, "status": response.status_code, "error": response.text}
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ CONNECTION ERROR - Could not connect to {BASE_URL}")
        print("Make sure the server is running!")
        return {"success": False, "error": "Connection error"}
    except Exception as e:
        print(f"\n❌ EXCEPTION: {type(e).__name__}: {e}")
        return {"success": False, "error": str(e)}


def test_with_username(username: str, password: str, user_type: str) -> Dict[str, Any]:
    """Test login endpoint with username instead of email."""
    url = f"{BASE_URL}/api/auth/login"
    
    payload = {
        "username": username,
        "password": password
    }
    
    print(f"\n{'='*60}")
    print(f"Testing {user_type} login with username: {username}")
    print(f"{'='*60}")
    print(f"POST {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ SUCCESS - {user_type} login with username successful!")
            user_info = data.get('user', {})
            print(f"  - Email: {user_info.get('email')}")
            print(f"  - Display Name: {user_info.get('display_name')}")
            print(f"  - Is Admin: {user_info.get('is_admin')}")
            return {"success": True, "data": data}
        else:
            print(f"\n❌ FAILED - Status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error: {response.text}")
            return {"success": False, "status": response.status_code, "error": response.text}
            
    except Exception as e:
        print(f"\n❌ EXCEPTION: {type(e).__name__}: {e}")
        return {"success": False, "error": str(e)}


def main():
    """Run all authentication tests."""
    print("="*60)
    print("Authentication Login Test Suite")
    print("="*60)
    
    # Test admin login
    admin_result = test_login("admin@demo.local", "admin123", "ADMIN")
    
    # Test regular user login
    user_result = test_login("user@demo.local", "user123", "REGULAR USER")
    
    # Test admin login with display name (username)
    admin_username_result = test_with_username("Admin User", "admin123", "ADMIN (by username)")
    
    # Test regular user login with display name (username)
    user_username_result = test_with_username("Regular User", "user123", "REGULAR USER (by username)")
    
    # Test invalid credentials
    print(f"\n{'='*60}")
    print("Testing invalid credentials (should fail)")
    print(f"{'='*60}")
    invalid_result = test_login("admin@demo.local", "wrongpassword", "INVALID")
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    results = [
        ("Admin Login (email)", admin_result.get("success", False)),
        ("Regular User Login (email)", user_result.get("success", False)),
        ("Admin Login (username)", admin_username_result.get("success", False)),
        ("Regular User Login (username)", user_username_result.get("success", False)),
        ("Invalid Credentials", not invalid_result.get("success", True)),  # Should fail
    ]
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    print(f"\n{'='*60}")
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1]
        print(f"Using custom base URL: {BASE_URL}")
    
    exit_code = main()
    sys.exit(exit_code)

