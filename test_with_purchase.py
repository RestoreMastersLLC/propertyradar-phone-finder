#!/usr/bin/env python3
"""
Test PropertyRadar API with Purchase=1 (WILL CHARGE ACCOUNT)

WARNING: This will charge your PropertyRadar account for the property search!
"""

import requests
import json

def test_with_real_purchase():
    test_address = "400 LAS COLINAS BLVD E, IRVING, TX 75039"
    api_key = "a1b7cec841201499fecdfcd9a7124217ed2d51ed"
    url = "https://api.propertyradar.com/v1/properties"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print(f"⚠️  WARNING: This will charge your PropertyRadar account!")
    print(f"📍 Address: {test_address}")
    print(f"💰 Setting Purchase=1 (real results, real charges)")
    print()
    
    params = {"Purchase": 1}  # REAL PURCHASE - WILL CHARGE!
    data = {
        "Criteria": [
            {
                "name": "Address",
                "value": [test_address]
            }
        ]
    }
    
    print(f"🔍 Making PropertyRadar API call with Purchase=1...")
    print(f"📤 Query: {params}")
    print(f"📤 Body: {json.dumps(data, indent=2)}")
    print()
    
    try:
        response = requests.post(url, headers=headers, json=data, params=params, timeout=30)
        
        if response.status_code == 200:
            response_data = response.json()
            
            print(f"✅ API Response Successful!")
            print(f"📊 Response structure:")
            print(f"   Top-level keys: {list(response_data.keys())}")
            
            if 'results' in response_data:
                results = response_data['results']
                print(f"   Number of results: {len(results)}")
                
                if results:
                    print(f"\n🎉 Found property data!")
                    
                    # Show full response structure
                    response_str = json.dumps(response_data, indent=2)
                    print(f"\n📄 Full response:")
                    if len(response_str) > 5000:
                        print(response_str[:5000] + "\n... (truncated)")
                    else:
                        print(response_str)
                    
                    # Analyze first result for owner information
                    first_result = results[0]
                    print(f"\n🔍 First property analysis:")
                    print(f"Property keys: {list(first_result.keys())}")
                    
                    # Look for owner and person key information
                    owner_related_keys = []
                    person_keys = []
                    
                    for key, value in first_result.items():
                        if any(keyword in key.lower() for keyword in ['owner', 'person', 'name']):
                            owner_related_keys.append((key, value))
                        if any(keyword in key.lower() for keyword in ['key', 'id']) and 'person' in key.lower():
                            person_keys.append((key, value))
                    
                    if owner_related_keys:
                        print(f"\n👤 Owner-related fields found:")
                        for key, value in owner_related_keys:
                            print(f"   {key}: {value}")
                    
                    if person_keys:
                        print(f"\n🔑 Person key fields found:")
                        for key, value in person_keys:
                            print(f"   {key}: {value}")
                    
                    return True, response_data
                else:
                    print(f"⚠️  No results found even with Purchase=1")
                    return False, response_data
            else:
                print(f"⚠️  No 'results' key in response")
                return False, response_data
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Error: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False, None

if __name__ == "__main__":
    print("⚠️  ⚠️  ⚠️  WARNING ⚠️  ⚠️  ⚠️")
    print("This script will charge your PropertyRadar account!")
    print("Only run if you want to pay for property data.")
    print("⚠️  ⚠️  ⚠️  ⚠️  ⚠️  ⚠️  ⚠️")
    print()
    
    # Uncomment the line below to actually run the test
    # success, data = test_with_real_purchase()
    
    print("Script ready but not executed.")
    print("Uncomment the test line if you want to make a paid API call.") 