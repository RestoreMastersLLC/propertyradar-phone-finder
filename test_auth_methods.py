#!/usr/bin/env python3
"""
Test Different Authentication Methods for PropertyRadar API
"""

import requests
import json

def test_property_radar_auth():
    test_address = "400 LAS COLINAS BLVD E, IRVING, TX 75039"
    api_key = "a1b7cec841201499fecdfcd9a7124217ed2d51ed"
    base_url = "https://api.propertyradar.com/v1"
    
    print(f"🔑 Testing different authentication methods for PropertyRadar API")
    print(f"📍 Address: {test_address}")
    print()
    
    # Test different authentication methods
    auth_tests = [
        {
            "name": "Bearer Token in Authorization Header",
            "headers": {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        },
        {
            "name": "API Key in Custom Header",
            "headers": {
                "X-API-Key": api_key,
                "Content-Type": "application/json"
            }
        },
        {
            "name": "API Key in Authorization Header (no Bearer)",
            "headers": {
                "Authorization": api_key,
                "Content-Type": "application/json"
            }
        },
        {
            "name": "API Key as Query Parameter",
            "headers": {
                "Content-Type": "application/json"
            },
            "extra_params": {"api_key": api_key}
        },
        {
            "name": "API Key as Query Parameter (key)",
            "headers": {
                "Content-Type": "application/json"
            },
            "extra_params": {"key": api_key}
        },
        {
            "name": "API Key in Body",
            "headers": {
                "Content-Type": "application/json"
            },
            "include_key_in_body": True
        }
    ]
    
    request_data = {
        "Criteria": [
            {
                "Name": "Address",
                "Value": [test_address]
            }
        ]
    }
    
    for i, auth_test in enumerate(auth_tests, 1):
        print(f"🔍 Test {i}: {auth_test['name']}")
        
        headers = auth_test["headers"]
        data = request_data.copy()
        params = {}
        
        # Add extra parameters if specified
        if "extra_params" in auth_test:
            params.update(auth_test["extra_params"])
        
        # Add API key to body if specified
        if auth_test.get("include_key_in_body"):
            data["api_key"] = api_key
        
        print(f"📤 Headers: {json.dumps(headers, indent=2)}")
        if params:
            print(f"📤 Params: {json.dumps(params, indent=2)}")
        
        try:
            url = f"{base_url}/properties"
            response = requests.post(url, headers=headers, json=data, params=params, timeout=30)
            
            print(f"📡 Response: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"✅ SUCCESS! Authentication method works!")
                print(f"Response preview: {json.dumps(response_data, indent=2)[:300]}...")
                return True
            elif response.status_code == 401:
                print(f"🔒 Unauthorized - API key issue")
            elif response.status_code == 403:
                print(f"🚫 Forbidden - Permission issue")
            elif response.status_code == 404:
                print(f"❓ Not found - Endpoint or auth issue")
            else:
                print(f"⚠️  Status {response.status_code}")
                
            # Show error details for debugging
            print(f"Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print("-" * 50)
    
    print("🔍 Trying alternative endpoints...")
    
    # Test different endpoints
    endpoints = [
        "/properties",
        "/search/properties", 
        "/v1/properties",
        "/property/search",
        "/property"
    ]
    
    for endpoint in endpoints:
        print(f"🔍 Testing endpoint: {endpoint}")
        try:
            url = f"https://api.propertyradar.com{endpoint}"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, headers=headers, json=request_data, timeout=30)
            print(f"📡 {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ SUCCESS with endpoint: {endpoint}")
                return True
            elif response.status_code != 404:
                print(f"   Response: {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
    
    print("🔍 All authentication and endpoint tests completed")
    return False

if __name__ == "__main__":
    test_property_radar_auth() 