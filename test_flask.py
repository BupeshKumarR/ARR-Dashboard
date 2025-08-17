#!/usr/bin/env python3
"""
Test script to verify Flask app endpoints
"""

import requests
import json

def test_flask_app():
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Flask App Endpoints")
    print("=" * 40)
    
    try:
        # Test main dashboard
        print("1. Testing main dashboard...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Dashboard loaded successfully")
            print(f"   Content length: {len(response.text)} characters")
        else:
            print(f"❌ Dashboard failed: {response.status_code}")
        
        # Test KPI endpoint
        print("\n2. Testing KPI endpoint...")
        response = requests.get(f"{base_url}/api/kpis")
        if response.status_code == 200:
            kpis = response.json()
            print("✅ KPI data retrieved successfully")
            print(f"   Current ARR: ${kpis['current_arr']:,.0f}")
            print(f"   Active Customers: {kpis['active_customers']}")
        else:
            print(f"❌ KPI endpoint failed: {response.status_code}")
        
        # Test waterfall endpoint
        print("\n3. Testing waterfall endpoint...")
        response = requests.get(f"{base_url}/api/waterfall")
        if response.status_code == 200:
            waterfall = response.json()
            print("✅ Waterfall data retrieved successfully")
            print(f"   Month: {waterfall['month']}")
            print(f"   Starting ARR: ${waterfall['starting_arr']:,.0f}")
        else:
            print(f"❌ Waterfall endpoint failed: {response.status_code}")
        
        # Test segments endpoint
        print("\n4. Testing segments endpoint...")
        response = requests.get(f"{base_url}/api/segments")
        if response.status_code == 200:
            segments = response.json()
            print("✅ Segments data retrieved successfully")
            print(f"   Number of segments: {len(segments)}")
        else:
            print(f"❌ Segments endpoint failed: {response.status_code}")
        
        print("\n🎉 All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app")
        print("💡 Make sure the Flask app is running: python3 app.py")
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_flask_app()
