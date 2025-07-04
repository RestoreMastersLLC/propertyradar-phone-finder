#!/usr/bin/env python3
"""
Test Different Purchase Parameter Formats for PropertyRadar API
"""

import requests
import json

def test_purchase_parameter():
    test_address = "400 LAS COLINAS BLVD E, IRVING, TX 75039"
    api_key = "a1b7cec841201499fecdfcd9a7124217ed2d51ed"
    url = "https://api.propertyradar.com/v1/properties"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print(f"🔑 Testing Purchase parameter formats for PropertyRadar API")
    print(f"📍 Address: {test_address}")
    print(f"🌐 URL: {url}")
    print()
    
    # Test different Purchase parameter formats
    test_cases = [
        {
            "name": "Purchase=0 at root level",
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
            "name": "Purchase=1 at root level",
            "data": {
                "Purchase": 1,
                "Criteria": [
                    {
                        "Name": "Address",
                        "Value": [test_address]
                    }
                ]
            }
        },
        {
            "name": "purchase=0 (lowercase)",
            "data": {
                "purchase": 0,
                "Criteria": [
                    {
                        "Name": "Address",
                        "Value": [test_address]
                    }
                ]
            }
        },
        {
            "name": "Purchase as string '0'",
            "data": {
                "Purchase": "0",
                "Criteria": [
                    {
                        "Name": "Address",
                        "Value": [test_address]
                    }
                ]
            }
        },
        {
            "name": "Purchase as string '1'",
            "data": {
                "Purchase": "1",
                "Criteria": [
                    {
                        "Name": "Address",
                        "Value": [test_address]
                    }
                ]
            }
        },
        {
            "name": "No Purchase, just Criteria",
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
            "name": "Purchase inside Criteria",
            "data": {
                "Criteria": [
                    {
                        "Name": "Address",
                        "Value": [test_address],
                        "Purchase": 0
                    }
                ]
            }
        },
        {
            "name": "Different structure - direct fields",
            "data": {
                "Address": test_address,
                "Purchase": 0
            }
        },
        {
            "name": "Query-style format",
            "data": {
                "query": {
                    "Address": test_address
                },
                "Purchase": 0
            }
        },
        {
            "name": "Search-style format",
            "data": {
                "search": {
                    "criteria": [
                        {
                            "field": "Address",
                            "value": test_address
                        }
                    ]
                },
                "Purchase": 0
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"🔍 Test {i}: {test_case['name']}")
        print(f"📤 Request: {json.dumps(test_case['data'], indent=2)}")
        
        try:
            response = requests.post(url, headers=headers, json=test_case['data'], timeout=30)
            
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
                        print(f"🏠 First property keys: {list(first_prop.keys())[:10]}...")
                        
                        # Look for owner info
                        owner_fields = ['Owner', 'owner', 'OwnerName', 'owners']
                        for field in owner_fields:
                            if field in first_prop:
                                print(f"👤 Found owner field '{field}': {first_prop[field]}")
                
                return True
            else:
                error_text = response.text
                print(f"❌ Status {response.status_code}: {error_text[:200]}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print("-" * 60)
    
    print("🔍 All Purchase parameter tests completed")
    return False

if __name__ == "__main__":
    test_purchase_parameter() 