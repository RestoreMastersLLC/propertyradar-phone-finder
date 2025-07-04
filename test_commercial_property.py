#!/usr/bin/env python3
"""
Systematic test of commercial property from GUI screenshot
400 LAS COLINAS BLVD E, IRVING, TX 75039

GUI shows:
- Property Type: Commercial
- Owner: NATHAN P PETROWSKY, 71
- Entity: CANAL CENTRE INVESTORS  
- Phones: 510-541-7382, 925-552-5886, 925-376-5886

Goal: Find the correct API parameters to get this same data
"""

import requests
import json
import re

def test_commercial_property_step_by_step():
    """Test the exact commercial property from GUI screenshot"""
    
    address = "400 LAS COLINAS BLVD E, IRVING, TX 75039"
    api_key = "a1b7cec841201499fecdfcd9a7124217ed2d51ed"
    
    print("🏢 SYSTEMATIC COMMERCIAL PROPERTY TEST")
    print("=" * 70)
    print(f"📍 Address: {address}")
    print(f"🎯 Expected from GUI:")
    print(f"   - Property Type: Commercial")
    print(f"   - Owner: NATHAN P PETROWSKY, 71")
    print(f"   - Entity: CANAL CENTRE INVESTORS")
    print(f"   - Phones: 510-541-7382, 925-552-5886, 925-376-5886")
    print("=" * 70)
    
    # Step 1: Property Search
    print(f"\n🔍 STEP 1: Property Search")
    properties = search_property(address, api_key)
    
    if not properties:
        print(f"❌ No properties found - cannot proceed")
        return
    
    # Step 2: Test all properties found
    for i, prop in enumerate(properties, 1):
        print(f"\n🏠 STEP 2.{i}: Testing Property {i}")
        test_property_owners(prop, api_key)

def search_property(address, api_key):
    """Search for the commercial property"""
    print(f"🔍 Searching for: {address}")
    
    # Parse address components
    components = {
        "street": "400 LAS COLINAS BLVD E",
        "city": "IRVING", 
        "state": "TX",
        "zip": "75039"
    }
    
    url = "https://api.propertyradar.com/v1/properties"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test both Purchase=0 and Purchase=1
    for purchase_mode in [0, 1]:
        print(f"\n   📡 Testing with Purchase={purchase_mode}")
        
        params = {"Purchase": purchase_mode}
        data = {
            "Criteria": [
                {"name": "Address", "value": [components['street']]},
                {"name": "City", "value": [components['city']]},
                {"name": "State", "value": [components['state']]},
                {"name": "ZipFive", "value": [components['zip']]}
            ]
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, params=params, timeout=30)
            print(f"   📡 Response: {response.status_code}")
            
            if response.status_code == 200:
                prop_data = response.json()
                total_cost = prop_data.get('totalCost', 0)
                result_count = prop_data.get('resultCount', 0)
                
                print(f"   💰 Cost: ${total_cost}")
                print(f"   📊 Properties: {result_count}")
                
                if 'results' in prop_data and prop_data['results']:
                    properties = prop_data['results']
                    print(f"   ✅ Found {len(properties)} property result(s)")
                    
                    for j, prop in enumerate(properties, 1):
                        radar_id = prop.get('RadarID')
                        prop_type = prop.get('AdvancedPropertyType', 'Unknown')
                        
                        print(f"   🏠 Property {j}: RadarID {radar_id}")
                        print(f"   📋 Type: {prop_type}")
                    
                    return properties
                else:
                    print(f"   ⚠️  No properties in results")
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    return None

def test_property_owners(property_data, api_key):
    """Test getting owners for a specific property"""
    radar_id = property_data.get('RadarID')
    prop_type = property_data.get('AdvancedPropertyType', 'Unknown')
    
    print(f"👤 Getting owners for RadarID: {radar_id}")
    print(f"📋 Property Type: {prop_type}")
    
    # Test different owner API approaches
    owner_endpoints = [
        f"https://api.propertyradar.com/v1/properties/{radar_id}/persons",
        f"https://api.propertyradar.com/v1/properties/{radar_id}/owners",
        f"https://api.propertyradar.com/v1/properties/{radar_id}",
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    for endpoint in owner_endpoints:
        print(f"\n   🔍 Testing endpoint: {endpoint}")
        
        # Test both Purchase modes
        for purchase_mode in [0, 1]:
            print(f"      📡 Purchase={purchase_mode}")
            
            params = {"Purchase": purchase_mode}
            
            try:
                response = requests.get(endpoint, headers=headers, params=params, timeout=30)
                print(f"      📡 Response: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    total_cost = data.get('totalCost', 0)
                    result_count = data.get('resultCount', 0)
                    
                    print(f"      💰 Cost: ${total_cost}")
                    print(f"      📊 Results: {result_count}")
                    
                    if 'results' in data and data['results']:
                        print(f"      ✅ SUCCESS! Found data:")
                        
                        for owner in data['results']:
                            person_key = owner.get('PersonKey')
                            name = owner.get('EntityName') or owner.get('Name') or 'Unknown'
                            person_type = owner.get('PersonType', 'Unknown')
                            
                            print(f"         👤 {name}")
                            print(f"         🔑 PersonKey: {person_key}")
                            print(f"         📋 Type: {person_type}")
                            
                            # If we found NATHAN P PETROWSKY or similar, test phone APIs
                            if person_key and ("NATHAN" in name.upper() or "PETROWSKY" in name.upper() or person_type == "Person"):
                                print(f"         🎯 Found individual person - testing phone API...")
                                test_phone_apis_comprehensive(person_key, name, api_key)
                    else:
                        print(f"      ⚠️  No results")
                        
                elif response.status_code == 400:
                    print(f"      ❌ 400 Error: {response.text[:100]}")
                else:
                    print(f"      ❌ Error: {response.status_code}")
                    
            except Exception as e:
                print(f"      ❌ Exception: {e}")

def test_phone_apis_comprehensive(person_key, owner_name, api_key):
    """Comprehensive test of phone APIs with different parameters"""
    print(f"\n         📞 COMPREHENSIVE PHONE API TEST")
    print(f"         👤 Owner: {owner_name}")
    print(f"         🔑 PersonKey: {person_key}")
    
    # Test different phone API variations
    phone_endpoints = [
        f"https://api.propertyradar.com/v1/persons/{person_key}/phone",
        f"https://api.propertyradar.com/v1/persons/{person_key}/Phone",
        f"https://api.propertyradar.com/v1/persons/{person_key}/phones",
        f"https://api.propertyradar.com/v1/persons/{person_key}/contact",
        f"https://api.propertyradar.com/v1/persons/{person_key}",
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test different parameter combinations
    param_combinations = [
        {"Purchase": 0},
        {"Purchase": 1},
        {"Purchase": "0"},
        {"Purchase": "1"},
        {"Purchase": 1, "format": "json"},
        {},  # No parameters
    ]
    
    for endpoint in phone_endpoints:
        print(f"\n            🔍 Endpoint: {endpoint.split('/')[-1]}")
        
        for params in param_combinations:
            param_str = str(params) if params else "No params"
            print(f"               📡 Params: {param_str}")
            
            # Test both GET and POST
            for method in ['GET', 'POST']:
                try:
                    if method == 'GET':
                        response = requests.get(endpoint, headers=headers, params=params, timeout=30)
                    else:
                        response = requests.post(endpoint, headers=headers, params=params, timeout=30)
                    
                    print(f"                  {method}: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Look for phone numbers in response
                        phones_found = find_phone_numbers_in_response(data)
                        if phones_found:
                            print(f"                  🎉 FOUND PHONES: {phones_found}")
                            
                            # Check if we found the expected numbers
                            expected_phones = ["510-541-7382", "925-552-5886", "925-376-5886"]
                            matches = [phone for phone in expected_phones if any(exp in str(phones_found) for exp in [phone.replace("-", ""), phone])]
                            if matches:
                                print(f"                  ✅ MATCHES GUI: {matches}")
                        else:
                            print(f"                  📄 Response: {json.dumps(data, indent=2)[:200]}...")
                            
                    elif response.status_code == 400:
                        error = response.text[:100]
                        if "not available" in error:
                            print(f"                  ⚠️  Not available: {error}")
                        else:
                            print(f"                  ❌ 400 Error: {error}")
                    else:
                        print(f"                  ❌ {response.status_code}")
                        
                except Exception as e:
                    print(f"                  ❌ Exception: {e}")

def find_phone_numbers_in_response(data):
    """Extract phone numbers from API response"""
    phones = []
    
    def search_recursive(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if any(phone_indicator in key.lower() for phone_indicator in ['phone', 'tel', 'mobile', 'landline']):
                    if isinstance(value, str) and any(char.isdigit() for char in value):
                        phones.append(value)
                elif isinstance(value, (dict, list)):
                    search_recursive(value)
        elif isinstance(obj, list):
            for item in obj:
                search_recursive(item)
    
    search_recursive(data)
    return phones

def main():
    """Main test function"""
    print("🧪 COMMERCIAL PROPERTY API REVERSE ENGINEERING")
    print("Testing exact address from GUI screenshot...")
    print()
    
    test_commercial_property_step_by_step()
    
    print("\n" + "=" * 70)
    print("🎯 This test will help us find:")
    print("   - Correct API endpoints for commercial properties")
    print("   - Right parameters for corporate vs individual owners")
    print("   - How to access phone data that GUI can see")
    print("=" * 70)

if __name__ == "__main__":
    main() 