#!/usr/bin/env python3
"""
Simple test script to verify the Flask app works locally
"""

import requests
import os
import sys

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get('http://localhost:5000/health')
        if response.status_code == 200:
            print("✅ Health endpoint working")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to localhost:5000")
        return False

def test_main_page():
    """Test the main page loads"""
    try:
        response = requests.get('http://localhost:5000/')
        if response.status_code == 200:
            print("✅ Main page loads successfully")
            return True
        else:
            print(f"❌ Main page failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to localhost:5000")
        return False

if __name__ == "__main__":
    print("Testing local Flask app...")
    print("Make sure the app is running with: python api/app.py")
    print()
    
    health_ok = test_health_endpoint()
    main_ok = test_main_page()
    
    if health_ok and main_ok:
        print("\n🎉 All tests passed! The app is ready for deployment.")
    else:
        print("\n❌ Some tests failed. Please check the app configuration.")
        sys.exit(1) 