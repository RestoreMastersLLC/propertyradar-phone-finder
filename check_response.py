#!/usr/bin/env python3
"""
Check PropertyRadar API Response Structure
"""

import requests
import json

def check_response():
    test_address = "400 LAS COLINAS BLVD E, IRVING, TX 75039"
    api_key = "a1b7cec841201499fecdfcd9a7124217ed2d51ed"
    url = "https://api.propertyradar.com/v1/properties"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    params = {"Purchase": 0}
    data = {
        "Criteria": [
            {
                "name": "Address",
                "value": [test_address]
            }
        ]
    }
    
    print(f"🔍 Analyzing PropertyRadar API response structure")
    print(f"📍 Address: {test_address}")
    print()
    
    try:
        response = requests.post(url, headers=headers, json=data, params=params, timeout=30)
        
        if response.status_code == 200:
            response_data = response.json()
            
            print(f"✅ API Response Successful!")
            print(f"📊 Response structure analysis:")
            print(f"   Top-level keys: {list(response_data.keys())}")
            print()
            
            # Show full response (with size limit)
            response_str = json.dumps(response_data, indent=2)
            if len(response_str) > 3000:
                print(f"📄 Response preview (first 3000 chars):")
                print(response_str[:3000] + "\n... (truncated)")
            else:
                print(f"📄 Full response:")
                print(response_str)
            
            print("\n" + "="*60)
            
            # Analyze structure in detail
            if 'results' in response_data:
                results = response_data['results']
                print(f"📊 Results analysis:")
                print(f"   Results type: {type(results)}")
                
                if isinstance(results, list):
                    print(f"   Number of results: {len(results)}")
                    
                    if results:
                        first_result = results[0]
                        print(f"   First result type: {type(first_result)}")
                        
                        if isinstance(first_result, dict):
                            print(f"   First result keys: {list(first_result.keys())}")
                            
                            # Look for property information
                            for key, value in first_result.items():
                                if isinstance(value, (str, int, float)):
                                    print(f"     {key}: {value}")
                                elif isinstance(value, list):
                                    print(f"     {key}: [list with {len(value)} items]")
                                    if value and isinstance(value[0], dict):
                                        print(f"       First item keys: {list(value[0].keys())}")
                                elif isinstance(value, dict):
                                    print(f"     {key}: dict with {len(value)} keys")
                                    print(f"       Keys: {list(value.keys())}")
                            
                            # Look specifically for owner/person information
                            print(f"\n🔍 Looking for owner/person information:")
                            owner_keywords = ['owner', 'person', 'name', 'key', 'id']
                            for key in first_result.keys():
                                for keyword in owner_keywords:
                                    if keyword.lower() in key.lower():
                                        print(f"   Found potential owner field: {key} = {first_result[key]}")
                
                elif isinstance(results, dict):
                    print(f"   Results keys: {list(results.keys())}")
                    for key, value in results.items():
                        print(f"     {key}: {type(value)} - {str(value)[:100]}...")
            
            print(f"\n🎯 Summary: PropertyRadar API is working with the correct format!")
            return True
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    check_response() 