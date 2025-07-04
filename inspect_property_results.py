#!/usr/bin/env python3
"""
Inspect PropertyRadar API response structure to understand
how to get owner information for addresses.
"""

import requests
import json

def inspect_property_result():
    """Inspect a single property result to understand the data structure"""
    
    # Test with the first Monday.com address
    api_key = "a1b7cec841201499fecdfcd9a7124217ed2d51ed"
    
    url = "https://api.propertyradar.com/v1/properties"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    params = {"Purchase": 1}
    
    # Test with first address: 1521 S Frontage Rd, Columbus, Ms 39701
    data = {
        "Criteria": [
            {
                "name": "Address",
                "value": ["1521 S Frontage Rd"]
            },
            {
                "name": "City",
                "value": ["Columbus"]
            },
            {
                "name": "State", 
                "value": ["MS"]
            },
            {
                "name": "ZipFive",
                "value": ["39701"]
            }
        ]
    }
    
    print("🔍 Inspecting PropertyRadar API response structure...")
    print("📍 Address: 1521 S Frontage Rd, Columbus, Ms 39701")
    print()
    
    try:
        response = requests.post(url, headers=headers, json=data, params=params, timeout=30)
        
        if response.status_code == 200:
            response_data = response.json()
            
            print("✅ API Response successful!")
            print(f"📊 Number of results: {len(response_data.get('results', []))}")
            print()
            
            if 'results' in response_data and response_data['results']:
                # Show full response structure
                print("📄 FULL RESPONSE STRUCTURE:")
                print("=" * 50)
                print(json.dumps(response_data, indent=2))
                print("=" * 50)
                
                # Analyze first result in detail
                first_result = response_data['results'][0]
                print("\n🔍 FIRST RESULT ANALYSIS:")
                print("=" * 50)
                
                print("📋 All available fields:")
                for key, value in first_result.items():
                    print(f"  {key}: {value}")
                
                print("\n🔑 Key fields for owner lookup:")
                potential_owner_keys = ['RadarID', 'PropertyID', 'ID', 'PersonKey', 'OwnerKey']
                for key in potential_owner_keys:
                    if key in first_result:
                        print(f"  ✅ {key}: {first_result[key]}")
                    else:
                        print(f"  ❌ {key}: Not found")
                
                # Try to get owner information using RadarID
                if 'RadarID' in first_result:
                    print(f"\n📞 Attempting to get owner information using RadarID...")
                    get_owner_by_radar_id(first_result['RadarID'], api_key)
                
            else:
                print("❌ No results found")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def get_owner_by_radar_id(radar_id, api_key):
    """Try to get owner information using RadarID"""
    print(f"🔍 Getting owner for RadarID: {radar_id}")
    
    # Try different endpoints that might contain owner information
    endpoints_to_try = [
        f"https://api.propertyradar.com/v1/properties/{radar_id}/owner",
        f"https://api.propertyradar.com/v1/properties/{radar_id}/persons",
        f"https://api.propertyradar.com/v1/properties/{radar_id}",
        f"https://api.propertyradar.com/v1/owners/{radar_id}",
        f"https://api.propertyradar.com/v1/persons/{radar_id}",
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    params = {"Purchase": 1}
    
    for endpoint in endpoints_to_try:
        print(f"\n🔍 Trying endpoint: {endpoint}")
        
        try:
            response = requests.get(endpoint, headers=headers, params=params, timeout=30)
            
            print(f"📡 Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success! Found owner data:")
                print(json.dumps(data, indent=2))
                return data
            else:
                print(f"❌ Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print(f"⚠️  Could not find owner information for RadarID: {radar_id}")
    return None

def check_api_documentation():
    """Check what endpoints are available"""
    print("\n📚 Checking PropertyRadar API documentation...")
    print("Based on typical PropertyRadar API structure:")
    print("1. Properties API: Get property details")
    print("2. Owners API: Get owner information")
    print("3. Persons API: Get person details and contact info")
    print("4. Relationships: Link properties to owners to persons")
    print()
    print("🔗 Typical flow:")
    print("  Property → RadarID → Owner → PersonKey → Person Details (phones)")

if __name__ == "__main__":
    inspect_property_result()
    check_api_documentation() 