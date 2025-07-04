#!/usr/bin/env python3
"""
Test PropertyRadar API with Address Components

Breaking down full addresses into separate criteria:
- Address (street only): "400 LAS COLINAS BLVD E"
- City: "IRVING"
- State: "TX" 
- ZipFive: "75039"
"""

import requests
import json
import re

def parse_address(full_address):
    """Parse full address into components"""
    # Try to extract components from full address
    # Format: "400 LAS COLINAS BLVD E, IRVING, TX 75039"
    
    parts = full_address.split(',')
    
    if len(parts) >= 3:
        street = parts[0].strip()
        city = parts[1].strip()
        
        # Extract state and ZIP from last part
        state_zip = parts[2].strip()
        state_zip_match = re.match(r'([A-Z]{2})\s+(\d{5})', state_zip)
        
        if state_zip_match:
            state = state_zip_match.group(1)
            zip_code = state_zip_match.group(2)
            
            return {
                "street": street,
                "city": city,
                "state": state,
                "zip": zip_code
            }
    
    return None

def test_address_components():
    test_address = "400 LAS COLINAS BLVD E, IRVING, TX 75039"
    api_key = "a1b7cec841201499fecdfcd9a7124217ed2d51ed"
    
    print(f"🔍 Testing PropertyRadar with address components:")
    print(f"📍 Full Address: {test_address}")
    
    # Parse address into components
    components = parse_address(test_address)
    
    if not components:
        print(f"❌ Could not parse address")
        return False
    
    print(f"🏠 Parsed components:")
    print(f"   Street: {components['street']}")
    print(f"   City: {components['city']}")
    print(f"   State: {components['state']}")
    print(f"   ZIP: {components['zip']}")
    print()
    
    url = "https://api.propertyradar.com/v1/properties"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    params = {"Purchase": 1}  # Paid search
    
    # Method 1: Use multiple criteria components
    data_components = {
        "Criteria": [
            {
                "name": "Address",      # Street only (no city/state/zip)
                "value": [components['street']]
            },
            {
                "name": "City",
                "value": [components['city']]
            },
            {
                "name": "State", 
                "value": [components['state']]
            },
            {
                "name": "ZipFive",
                "value": [components['zip']]
            }
        ]
    }
    
    print(f"🔍 Method 1: Using separate address components")
    print(f"📤 Request: {json.dumps(data_components, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=data_components, params=params, timeout=30)
        
        print(f"📡 Response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS with address components!")
            
            if 'results' in data and data['results']:
                results = data['results']
                print(f"📊 Found {len(results)} property result(s)")
                
                # Show first result
                if results:
                    first_result = results[0]
                    print(f"\n🏠 First result keys: {list(first_result.keys())}")
                    
                    # Look for owner information
                    owner_fields = ['Owner', 'owner', 'OwnerName', 'owner_name', 'Name', 'name']
                    for field in owner_fields:
                        if field in first_result:
                            print(f"👤 {field}: {first_result[field]}")
                    
                    # Look for person keys for phone lookup
                    key_fields = ['PersonKey', 'person_key', 'OwnerKey', 'owner_key']
                    for field in key_fields:
                        if field in first_result:
                            print(f"🔑 {field}: {first_result[field]}")
                
                return True
            else:
                print(f"⚠️  No results found")
                print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Details: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False
    
    return False

def test_alternatives():
    """Test alternative approaches"""
    test_address = "400 LAS COLINAS BLVD E, IRVING, TX 75039"
    api_key = "a1b7cec841201499fecdfcd9a7124217ed2d51ed"
    
    url = "https://api.propertyradar.com/v1/properties"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    params = {"Purchase": 1}
    
    alternatives = [
        {
            "name": "Just Address field",
            "data": {
                "Criteria": [
                    {
                        "name": "Address",
                        "value": ["400 LAS COLINAS BLVD E"]  # Street only
                    }
                ]
            }
        },
        {
            "name": "Street Name only",
            "data": {
                "Criteria": [
                    {
                        "name": "SiteStreetName",
                        "value": ["LAS COLINAS"]
                    }
                ]
            }
        },
        {
            "name": "Address Number + Street Name",
            "data": {
                "Criteria": [
                    {
                        "name": "SiteNumber",
                        "value": [[400, 400]]  # Range format
                    },
                    {
                        "name": "SiteStreetName", 
                        "value": ["LAS COLINAS"]
                    }
                ]
            }
        }
    ]
    
    for i, test in enumerate(alternatives, 1):
        print(f"\n🔍 Alternative {i}: {test['name']}")
        print(f"📤 Request: {json.dumps(test['data'], indent=2)}")
        
        try:
            response = requests.post(url, headers=headers, json=test['data'], params=params, timeout=30)
            print(f"📡 Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'results' in data and data['results']:
                    print(f"✅ SUCCESS! Found {len(data['results'])} result(s)")
                    return True
                else:
                    print(f"⚠️  No results")
            else:
                print(f"❌ Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    return False

if __name__ == "__main__":
    print("🚀 Testing PropertyRadar API with proper address format")
    print("=" * 60)
    
    success1 = test_address_components()
    
    if not success1:
        print("\n" + "=" * 60)
        print("🔄 Trying alternative approaches...")
        success2 = test_alternatives()
        
        if not success2:
            print("\n❌ All methods failed")
    else:
        print("\n🎉 Success with address components!") 