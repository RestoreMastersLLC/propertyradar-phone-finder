#!/usr/bin/env python3
"""
Test PropertyRadar Phone API endpoints to find the correct format
"""

import requests
import json

def test_phone_api_endpoints():
    """Test different phone API endpoint formats"""
    
    # Use the PersonKey we found: p658049745
    person_key = "p658049745"
    api_key = "a1b7cec841201499fecdfcd9a7124217ed2d51ed"
    
    print(f"📞 Testing phone API endpoints for PersonKey: {person_key}")
    print()
    
    # Try different possible phone API endpoints
    endpoints_to_test = [
        f"https://api.propertyradar.com/v1/persons/{person_key}/phone",
        f"https://api.propertyradar.com/v1/persons/{person_key}/phones",
        f"https://api.propertyradar.com/v1/persons/{person_key}/contact",
        f"https://api.propertyradar.com/v1/persons/{person_key}/contacts",
        f"https://api.propertyradar.com/v1/persons/{person_key}",
        f"https://api.propertyradar.com/v1/person/{person_key}/phone",
        f"https://api.propertyradar.com/v1/person/{person_key}",
        f"https://api.propertyradar.com/v1/contacts/{person_key}",
        f"https://api.propertyradar.com/v1/phone/{person_key}",
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test both GET and POST methods
    for endpoint in endpoints_to_test:
        print(f"🔍 Testing endpoint: {endpoint}")
        
        # Test GET method
        try:
            response = requests.get(endpoint, headers=headers, params={"Purchase": 1}, timeout=30)
            print(f"  GET Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ GET Success! Response:")
                print(f"  {json.dumps(data, indent=2)}")
                return endpoint, data
            elif response.status_code != 404:
                print(f"  ⚠️  GET Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"  ❌ GET Exception: {e}")
        
        # Test POST method
        try:
            response = requests.post(endpoint, headers=headers, params={"Purchase": 1}, timeout=30)
            print(f"  POST Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ POST Success! Response:")
                print(f"  {json.dumps(data, indent=2)}")
                return endpoint, data
            elif response.status_code != 404:
                print(f"  ⚠️  POST Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"  ❌ POST Exception: {e}")
        
        print()
    
    print("❌ No working phone API endpoint found")
    return None, None

def test_person_details_api():
    """Test getting person details which might include phone numbers"""
    
    person_key = "p658049745"
    api_key = "a1b7cec841201499fecdfcd9a7124217ed2d51ed"
    
    print(f"👤 Testing person details API for PersonKey: {person_key}")
    
    url = f"https://api.propertyradar.com/v1/persons/{person_key}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, params={"Purchase": 1}, timeout=30)
        print(f"📡 Person Details API response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Person details:")
            print(json.dumps(data, indent=2))
            
            # Look for phone numbers in the response
            print(f"\n📞 Looking for phone numbers in person details:")
            find_phone_numbers_in_response(data)
            
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def find_phone_numbers_in_response(data):
    """Recursively search for phone numbers in API response"""
    phones = []
    
    def search_recursive(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                if 'phone' in key.lower() and value:
                    phones.append((current_path, value))
                    print(f"  📞 Found phone at {current_path}: {value}")
                elif isinstance(value, (dict, list)):
                    search_recursive(value, current_path)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                current_path = f"{path}[{i}]" if path else f"[{i}]"
                search_recursive(item, current_path)
    
    search_recursive(data)
    
    if not phones:
        print("  ⚠️  No phone numbers found in response")
    
    return phones

if __name__ == "__main__":
    print("🚀 Testing PropertyRadar Phone API endpoints")
    print("=" * 60)
    
    # Test different phone API endpoints
    working_endpoint, phone_data = test_phone_api_endpoints()
    
    if not working_endpoint:
        print("\n" + "=" * 60)
        print("🔄 Testing person details API...")
        test_person_details_api()
    
    print("\n🎯 Phone API testing completed!") 