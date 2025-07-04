#!/usr/bin/env python3
"""
Test script for single address: 3910 Highway 45 N, Columbus, Ms 39705
Tests the smart cached data retrieval logic
"""

import requests
import json
import re
from datetime import datetime

def parse_address(full_address):
    """Parse full address into components for PropertyRadar API"""
    parts = full_address.split(',')
    
    if len(parts) >= 3:
        street = parts[0].strip()
        city = parts[1].strip()
        
        # Extract state and ZIP from last part
        state_zip = parts[2].strip()
        state_zip_match = re.match(r'([A-Za-z]{2})\s+(\d{5})', state_zip)
        
        if state_zip_match:
            state = state_zip_match.group(1).upper()
            zip_code = state_zip_match.group(2)
            
            return {
                "street": street,
                "city": city,
                "state": state,
                "zip": zip_code
            }
    
    return None

def search_property_with_propertyradar(address, api_key):
    """Search for property using PropertyRadar API"""
    print(f"🔍 Searching PropertyRadar for: {address}")
    
    components = parse_address(address)
    if not components:
        print(f"❌ Could not parse address: {address}")
        return []
    
    print(f"🏠 Parsed components:")
    print(f"   Street: {components['street']}")
    print(f"   City: {components['city']}")
    print(f"   State: {components['state']}")
    print(f"   ZIP: {components['zip']}")
    
    url = "https://api.propertyradar.com/v1/properties"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    params = {"Purchase": 1}  # Paid search for real results
    
    request_data = {
        "Criteria": [
            {
                "name": "Address",
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
    
    try:
        response = requests.post(url, headers=headers, json=request_data, params=params, timeout=30)
        print(f"📡 PropertyRadar response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            total_cost = data.get('totalCost', 0)
            result_count = data.get('resultCount', 0)
            
            print(f"💰 Property Search Cost: ${total_cost}")
            print(f"📊 Properties Found: {result_count}")
            
            if 'results' in data and data['results']:
                print(f"✅ Found {len(data['results'])} property result(s)")
                return data['results']
            else:
                print(f"⚠️  No properties found for this address")
                return []
        else:
            print(f"❌ PropertyRadar error: {response.status_code}")
            print(f"Error: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Error searching PropertyRadar: {e}")
        return []

def get_owners_by_radar_id(radar_id, api_key):
    """Get owner information using PropertyRadar Persons API"""
    print(f"👤 Getting owners for RadarID: {radar_id}")
    
    url = f"https://api.propertyradar.com/v1/properties/{radar_id}/persons"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    params = {"Purchase": 1}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f"📡 Owners API response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            total_cost = data.get('totalCost', 0)
            result_count = data.get('resultCount', 0)
            
            print(f"💰 Owners Search Cost: ${total_cost}")
            print(f"📊 Owners Found: {result_count}")
            
            if 'results' in data and data['results']:
                print(f"✅ Found {len(data['results'])} owner(s)")
                
                owners = []
                for owner in data['results']:
                    owner_info = {
                        "person_key": owner.get('PersonKey'),
                        "name": owner.get('EntityName') or owner.get('Name') or 'Unknown Owner',
                        "ownership_role": owner.get('OwnershipRole', 'Unknown'),
                        "person_type": owner.get('PersonType', 'Unknown'),
                    }
                    owners.append(owner_info)
                    
                    print(f"👤 Owner: {owner_info['name']}")
                    print(f"🔑 PersonKey: {owner_info['person_key']}")
                    print(f"📋 Type: {owner_info['person_type']}")
                    print(f"📍 Role: {owner_info['ownership_role']}")
                    
                return owners
            else:
                print(f"⚠️  No owners found in API response")
                return []
        else:
            print(f"❌ Owners API error: {response.status_code}")
            print(f"Error: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Error getting owners: {e}")
        return []

def get_cached_phone_data(person_key, api_key, url, headers):
    """Try to get already-purchased phone data using Purchase=0"""
    print(f"🔄 Checking cached phone data (Purchase=0)...")
    
    params = {"Purchase": 0}
    
    try:
        response = requests.post(url, headers=headers, params=params, timeout=30)
        print(f"📡 Cached data response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            total_cost = data.get('totalCost', 0)
            result_count = data.get('resultCount', 0)
            
            print(f"💰 Cached data cost: ${total_cost}")
            print(f"📊 Cached records: {result_count}")
            
            # Search for phone numbers comprehensively
            phones = find_phone_numbers_in_response_comprehensive(data)
            
            if phones:
                print(f"✅ Retrieved {len(phones)} cached phone number(s)")
                for phone in phones:
                    print(f"   📞 {phone}")
                return phones, float(total_cost)
            else:
                print(f"⚠️  No phones in cached data")
                if result_count > 0:
                    print(f"📄 Raw response structure:")
                    print(f"   Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    if 'results' in data:
                        print(f"   Results: {len(data['results'])} items")
                        if data['results']:
                            print(f"   First result keys: {list(data['results'][0].keys()) if isinstance(data['results'][0], dict) else 'Not a dict'}")
                            # Print first result to see what's there
                            print(f"   First result sample: {json.dumps(data['results'][0], indent=2)}")
                
        else:
            print(f"❌ Cached data error: {response.status_code}")
            if response.status_code == 400:
                print(f"   Error message: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting cached data: {e}")
    
    return [], 0

def find_phone_numbers_in_response_comprehensive(data):
    """Comprehensive search for phone numbers in any API response"""
    phones = []
    
    def search_recursive(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                
                # Look for phone-related keys
                phone_indicators = ['phone', 'tel', 'mobile', 'landline', 'number', 'linktext']
                if any(indicator in key.lower() for indicator in phone_indicators):
                    if isinstance(value, str) and any(char.isdigit() for char in value):
                        # Extract phone number from string
                        phone_match = re.search(r'(\d{3}[-.]?\d{3}[-.]?\d{4})', value)
                        if phone_match:
                            phones.append(phone_match.group(1))
                            print(f"   📞 Found phone in {current_path}: {phone_match.group(1)}")
                    elif isinstance(value, (list, dict)):
                        search_recursive(value, current_path)
                elif isinstance(value, (dict, list)):
                    search_recursive(value, current_path)
                    
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                current_path = f"{path}[{i}]" if path else f"[{i}]"
                search_recursive(item, current_path)
    
    search_recursive(data)
    
    # Clean and format found phone numbers
    cleaned_phones = []
    for phone in set(phones):  # Remove duplicates
        # Extract just digits
        digits = ''.join(c for c in phone if c.isdigit())
        if len(digits) == 10:
            formatted = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
            cleaned_phones.append(formatted)
        elif len(digits) == 11 and digits.startswith('1'):
            formatted = f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
            cleaned_phones.append(formatted)
        elif len(digits) >= 10:
            cleaned_phones.append(phone)
    
    return cleaned_phones

def get_phone_numbers_smart(person_key, api_key):
    """Smart phone number retrieval - Check cached data FIRST"""
    if not person_key:
        print(f"⚠️  No PersonKey available - cannot get phone numbers")
        return [], 0
    
    print(f"📞 Getting phone numbers for PersonKey: {person_key}")
    
    url = f"https://api.propertyradar.com/v1/persons/{person_key}/Phone"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Strategy 1: Try to get already-purchased data FIRST (Purchase=0)
    print(f"🔄 Step 1: Checking for already-purchased phone data (Purchase=0)...")
    cached_phones, cached_cost = get_cached_phone_data(person_key, api_key, url, headers)
    if cached_phones:
        return cached_phones, cached_cost
    
    # Strategy 2: Only try to purchase new data if no cached data found (Purchase=1)
    print(f"💰 Step 2: No cached data found - trying to purchase new phone data...")
    params = {"Purchase": 1}
    
    try:
        response = requests.post(url, headers=headers, params=params, timeout=30)
        print(f"📡 Phone API response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            total_cost = data.get('totalCost', 0)
            result_count = data.get('resultCount', 0)
            
            print(f"💰 Phone API Cost: ${total_cost}")
            print(f"📊 Phone Records: {result_count}")
            
            phones = find_phone_numbers_in_response_comprehensive(data)
            
            if phones:
                print(f"✅ Found {len(phones)} phone number(s) via purchase")
                for phone in phones:
                    print(f"   📞 {phone}")
                return phones, float(total_cost)
            else:
                print(f"⚠️  No phone numbers found in purchase response")
                if result_count > 0:
                    print(f"📄 Purchase response structure:")
                    print(f"   Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    if 'results' in data:
                        print(f"   Results: {len(data['results'])} items")
                        if data['results']:
                            print(f"   First result sample: {json.dumps(data['results'][0], indent=2)}")
            
            return phones, float(total_cost)
            
        elif response.status_code == 400:
            error_msg = response.text
            if "already purchased" in error_msg or "not available for purchase" in error_msg:
                print(f"💡 Data already purchased but couldn't retrieve via cached methods")
                print(f"⚠️  Error: {error_msg}")
                return [], 0
            else:
                print(f"❌ Phone API error: {response.status_code}")
                print(f"Error: {response.text}")
                return [], 0
        else:
            print(f"❌ Phone API error: {response.status_code}")
            print(f"Error: {response.text}")
            return [], 0
            
    except Exception as e:
        print(f"❌ Error getting phone numbers: {e}")
        return [], 0

def main():
    """Test the smart cached data retrieval with single address"""
    
    # Configuration
    API_KEY = "a1b7cec841201499fecdfcd9a7124217ed2d51ed"
    TEST_ADDRESS = "415 E Davis St, Luling, Tx 78648"
    
    print("🚀 Testing Smart Cached Data Retrieval")
    print("=" * 60)
    print(f"📍 Test Address: {TEST_ADDRESS}")
    print("=" * 60)
    print()
    
    # Step 1: Search for property
    print("📋 Step 1: Searching for property...")
    print("-" * 40)
    property_results = search_property_with_propertyradar(TEST_ADDRESS, API_KEY)
    
    if not property_results:
        print("❌ No property found - cannot test phone/email retrieval")
        return
    
    print()
    
    # Step 2: Get owners
    print("📋 Step 2: Getting property owners...")
    print("-" * 40)
    
    all_owners = []
    for result in property_results:
        radar_id = result.get('RadarID')
        if radar_id:
            owners = get_owners_by_radar_id(radar_id, API_KEY)
            all_owners.extend(owners)
    
    if not all_owners:
        print("❌ No owners found - cannot test phone/email retrieval")
        return
    
    print()
    
    # Step 3: Test smart phone retrieval for each owner
    print("📋 Step 3: Testing smart phone number retrieval...")
    print("-" * 40)
    
    for i, owner in enumerate(all_owners, 1):
        print(f"\n👤 Owner {i}/{len(all_owners)}: {owner['name']}")
        person_key = owner.get('person_key')
        
        if person_key:
            phones, cost = get_phone_numbers_smart(person_key, API_KEY)
            print(f"📞 Result: {len(phones)} phone(s), Cost: ${cost}")
            
            if phones:
                print(f"🎉 SUCCESS! Found phone numbers:")
                for phone in phones:
                    print(f"   📞 {phone}")
            else:
                print(f"⚠️  No phone numbers found for {owner['name']}")
        else:
            print(f"❌ No PersonKey for {owner['name']}")
        
        print()
    
    print("=" * 60)
    print("🎯 Smart cached data retrieval test completed!")

if __name__ == "__main__":
    main() 