#!/usr/bin/env python3
"""
Test Working PropertyRadar API Format
Purchase = query parameter
Criteria = request body (fix structure)
"""

import requests
import json

def test_working_format():
    test_address = "400 LAS COLINAS BLVD E, IRVING, TX 75039"
    api_key = "a1b7cec841201499fecdfcd9a7124217ed2d51ed"
    url = "https://api.propertyradar.com/v1/properties"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print(f"🔑 Testing working PropertyRadar API format")
    print(f"📍 Address: {test_address}")
    print(f"🌐 URL: {url}")
    print()
    
    # Test different Criteria structures with Purchase in query
    test_cases = [
        {
            "name": "lowercase name field",
            "params": {"Purchase": 0},
            "data": {
                "Criteria": [
                    {
                        "name": "Address",  # lowercase
                        "value": [test_address]  # lowercase
                    }
                ]
            }
        },
        {
            "name": "lowercase name, uppercase Value",
            "params": {"Purchase": 0},
            "data": {
                "Criteria": [
                    {
                        "name": "Address",  # lowercase
                        "Value": [test_address]  # uppercase
                    }
                ]
            }
        },
        {
            "name": "uppercase Name, lowercase value",
            "params": {"Purchase": 0},
            "data": {
                "Criteria": [
                    {
                        "Name": "Address",  # uppercase
                        "value": [test_address]  # lowercase
                    }
                ]
            }
        },
        {
            "name": "field instead of name",
            "params": {"Purchase": 0},
            "data": {
                "Criteria": [
                    {
                        "field": "Address",
                        "value": [test_address]
                    }
                ]
            }
        },
        {
            "name": "type and value",
            "params": {"Purchase": 0},
            "data": {
                "Criteria": [
                    {
                        "type": "Address",
                        "value": [test_address]
                    }
                ]
            }
        },
        {
            "name": "key and value",
            "params": {"Purchase": 0},
            "data": {
                "Criteria": [
                    {
                        "key": "Address",
                        "value": [test_address]
                    }
                ]
            }
        },
        {
            "name": "criteria instead of Criteria",
            "params": {"Purchase": 0},
            "data": {
                "criteria": [  # lowercase
                    {
                        "name": "Address",
                        "value": [test_address]
                    }
                ]
            }
        },
        {
            "name": "SiteAddress field",
            "params": {"Purchase": 0},
            "data": {
                "Criteria": [
                    {
                        "name": "SiteAddress",
                        "value": [test_address]
                    }
                ]
            }
        },
        {
            "name": "Purchase=1 with working format",
            "params": {"Purchase": 1},
            "data": {
                "Criteria": [
                    {
                        "name": "Address",
                        "value": [test_address]
                    }
                ]
            }
        },
        {
            "name": "Multiple criteria formats",
            "params": {"Purchase": 0},
            "data": {
                "Criteria": [
                    {
                        "name": "Address",
                        "value": [test_address]
                    },
                    {
                        "name": "SiteAddress", 
                        "value": [test_address]
                    }
                ]
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"🔍 Test {i}: {test_case['name']}")
        print(f"📤 Query: {test_case['params']}")
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
                print(f"🎉 SUCCESS! PropertyRadar API is working!")
                print(f"Response keys: {list(data.keys())}")
                
                # Look for properties in response
                if 'Properties' in data or 'properties' in data:
                    properties = data.get('Properties', data.get('properties', []))
                    print(f"📊 Found {len(properties)} properties")
                    
                    if properties:
                        first_prop = properties[0]
                        print(f"🏠 First property keys: {list(first_prop.keys())}")
                        
                        # Look for owner information
                        owner_fields = ['Owner', 'owner', 'OwnerName', 'owners', 'PropertyOwner']
                        for field in owner_fields:
                            if field in first_prop:
                                print(f"👤 Owner field '{field}': {first_prop[field]}")
                        
                        # Look for PersonKey for phone lookup
                        person_key_fields = ['PersonKey', 'person_key', 'OwnerKey', 'owner_key']
                        for field in person_key_fields:
                            if field in first_prop:
                                print(f"🔑 Person key field '{field}': {first_prop[field]}")
                
                return True, test_case
            else:
                error_text = response.text
                print(f"❌ Error: {error_text[:300]}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print("-" * 60)
    
    print("🔍 All format tests completed")
    return False, None

if __name__ == "__main__":
    success, working_format = test_working_format()
    if success:
        print(f"\n🎉 WORKING FORMAT FOUND!")
        print(f"Format: {working_format['name']}")
        print(f"Query: {working_format['params']}")
        print(f"Body: {json.dumps(working_format['data'], indent=2)}")
    else:
        print(f"\n❌ No working format found yet") 