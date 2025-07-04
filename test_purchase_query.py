#!/usr/bin/env python3
"""
Test Purchase Parameter as Query Parameter for PropertyRadar API
"""

import requests
import json

def test_purchase_as_query():
    test_address = "400 LAS COLINAS BLVD E, IRVING, TX 75039"
    api_key = "a1b7cec841201499fecdfcd9a7124217ed2d51ed"
    url = "https://api.propertyradar.com/v1/properties"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print(f"🔑 Testing Purchase as query parameter for PropertyRadar API")
    print(f"📍 Address: {test_address}")
    print(f"🌐 URL: {url}")
    print()
    
    # Test Purchase as query parameter
    test_cases = [
        {
            "name": "Purchase=0 as query param",
            "params": {"Purchase": 0},
            "data": {
                "Criteria": [
                    {
                        "Name": "Address",
                        "Value": [test_address]
                    }
                ]
            }
        },
        {
            "name": "Purchase=1 as query param",
            "params": {"Purchase": 1},
            "data": {
                "Criteria": [
                    {
                        "Name": "Address",
                        "Value": [test_address]
                    }
                ]
            }
        },
        {
            "name": "purchase=0 as query param (lowercase)",
            "params": {"purchase": 0},
            "data": {
                "Criteria": [
                    {
                        "Name": "Address",
                        "Value": [test_address]
                    }
                ]
            }
        },
        {
            "name": "Both Purchase in query and body",
            "params": {"Purchase": 0},
            "data": {
                "Purchase": 0,
                "Criteria": [
                    {
                        "Name": "Address",
                        "Value": [test_address]
                    }
                ]
            }
        },
        {
            "name": "Empty body with Purchase query",
            "params": {"Purchase": 0},
            "data": {}
        },
        {
            "name": "Address as query param too",
            "params": {
                "Purchase": 0,
                "Address": test_address
            },
            "data": {}
        },
        {
            "name": "Different param names",
            "params": {
                "buy": 0,
                "address": test_address
            },
            "data": {}
        },
        {
            "name": "Test mode parameter",
            "params": {
                "test": 1,
                "Purchase": 0
            },
            "data": {
                "Criteria": [
                    {
                        "Name": "Address",
                        "Value": [test_address]
                    }
                ]
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"🔍 Test {i}: {test_case['name']}")
        print(f"📤 Query Params: {test_case['params']}")
        print(f"📤 Body: {json.dumps(test_case['data'], indent=2)}")
        
        try:
            response = requests.post(url, 
                                   headers=headers, 
                                   json=test_case['data'], 
                                   params=test_case['params'], 
                                   timeout=30)
            
            print(f"📡 Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS! This format works!")
                print(f"Response preview: {json.dumps(data, indent=2)[:500]}...")
                
                # Look for properties in response
                if 'Properties' in data or 'properties' in data:
                    properties = data.get('Properties', data.get('properties', []))
                    print(f"📊 Found {len(properties)} properties")
                    
                    if properties:
                        first_prop = properties[0]
                        print(f"🏠 Property found!")
                        print(f"Property keys: {list(first_prop.keys())[:10]}...")
                
                return True
            elif response.status_code in [400, 401, 403, 404]:
                error_text = response.text
                print(f"❌ Error: {error_text[:250]}")
            else:
                print(f"⚠️  Status {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print("-" * 60)
    
    print("🔍 All query parameter tests completed")
    
    # Also test GET request
    print("\n🔍 Testing GET request...")
    try:
        params = {
            "Purchase": 0,
            "Address": test_address
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f"📡 GET Response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ GET SUCCESS!")
            print(f"Response: {json.dumps(data, indent=2)[:300]}...")
            return True
        else:
            print(f"❌ GET Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ GET Exception: {e}")
    
    return False

if __name__ == "__main__":
    test_purchase_as_query() 