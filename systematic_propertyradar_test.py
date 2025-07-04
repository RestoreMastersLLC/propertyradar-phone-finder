#!/usr/bin/env python3
"""
Systematic PropertyRadar API Test
- Test both commercial and residential addresses
- Track costs and charges for each API call
- Monitor what's actually working vs failing
- Reverse engineer the exact process
"""

import requests
import json
import re
import time
from datetime import datetime

def parse_address(full_address):
    """Parse full address into components for PropertyRadar API"""
    parts = full_address.split(',')
    
    if len(parts) >= 3:
        street = parts[0].strip()
        city = parts[1].strip()
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
    
    # Handle other formats
    if len(parts) >= 2:
        street = parts[0].strip()
        city_state_zip = parts[1].strip()
        city_state_zip_match = re.match(r'(.+?),?\s+([A-Za-z]{2})\s+(\d{5})', city_state_zip)
        
        if city_state_zip_match:
            city = city_state_zip_match.group(1).strip()
            state = city_state_zip_match.group(2).upper()
            zip_code = city_state_zip_match.group(3)
            
            return {
                "street": street,
                "city": city,
                "state": state,
                "zip": zip_code
            }
    
    return None

def test_property_search(address, api_key):
    """Test property search and track response"""
    print(f"\n🏠 TESTING ADDRESS: {address}")
    print("=" * 70)
    
    components = parse_address(address)
    if not components:
        print(f"❌ Could not parse address")
        return None
    
    print(f"📍 Parsed: {components['street']}, {components['city']}, {components['state']} {components['zip']}")
    
    # Step 1: Property Search
    url = "https://api.propertyradar.com/v1/properties"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    params = {"Purchase": 1}
    data = {
        "Criteria": [
            {"name": "Address", "value": [components['street']]},
            {"name": "City", "value": [components['city']]},
            {"name": "State", "value": [components['state']]},
            {"name": "ZipFive", "value": [components['zip']]}
        ]
    }
    
    print(f"🔍 Step 1: Property Search...")
    
    try:
        response = requests.post(url, headers=headers, json=data, params=params, timeout=30)
        print(f"📡 Response: {response.status_code}")
        
        if response.status_code == 200:
            prop_data = response.json()
            
            # Track costs from property search
            total_cost = prop_data.get('totalCost', 0)
            result_count = prop_data.get('resultCount', 0)
            
            print(f"💰 Property Search Cost: ${total_cost}")
            print(f"📊 Properties Found: {result_count}")
            
            if 'results' in prop_data and prop_data['results']:
                print(f"✅ Found {len(prop_data['results'])} property result(s)")
                
                # Test each property for owners
                for i, property_result in enumerate(prop_data['results'][:2], 1):  # Limit to 2 properties
                    radar_id = property_result.get('RadarID')
                    property_type = property_result.get('AdvancedPropertyType', 'Unknown')
                    
                    print(f"\n   🏠 Property {i}: RadarID {radar_id}")
                    print(f"   📋 Type: {property_type}")
                    
                    if radar_id:
                        # Step 2: Get owners for this property
                        owners = test_owners_search(radar_id, api_key)
                        
                        if owners:
                            # Step 3: Test phone/email for each owner
                            for owner in owners[:2]:  # Limit to 2 owners per property
                                test_contact_apis(owner, api_key)
                
                return prop_data
            else:
                print(f"⚠️  No properties found")
                return prop_data
        else:
            print(f"❌ Property search failed: {response.status_code}")
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Property search exception: {e}")
        return None

def test_owners_search(radar_id, api_key):
    """Test owners search for a property"""
    print(f"\n   👤 Step 2: Getting owners for RadarID {radar_id}...")
    
    url = f"https://api.propertyradar.com/v1/properties/{radar_id}/persons"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    params = {"Purchase": 1}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f"   📡 Response: {response.status_code}")
        
        if response.status_code == 200:
            owners_data = response.json()
            
            # Track costs from owners search
            total_cost = owners_data.get('totalCost', 0)
            result_count = owners_data.get('resultCount', 0)
            
            print(f"   💰 Owners Search Cost: ${total_cost}")
            print(f"   📊 Owners Found: {result_count}")
            
            if 'results' in owners_data and owners_data['results']:
                owners = []
                for owner in owners_data['results']:
                    owner_info = {
                        "person_key": owner.get('PersonKey'),
                        "name": owner.get('EntityName') or owner.get('Name') or 'Unknown Owner',
                        "person_type": owner.get('PersonType', 'Unknown'),
                        "ownership_role": owner.get('OwnershipRole', 'Unknown')
                    }
                    owners.append(owner_info)
                    
                    print(f"   👤 Owner: {owner_info['name']}")
                    print(f"   🔑 PersonKey: {owner_info['person_key']}")
                    print(f"   📋 Type: {owner_info['person_type']}")
                
                return owners
            else:
                print(f"   ⚠️  No owners found")
                return []
        else:
            print(f"   ❌ Owners search failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return []
            
    except Exception as e:
        print(f"   ❌ Owners search exception: {e}")
        return []

def test_contact_apis(owner, api_key):
    """Test phone and email APIs for an owner"""
    person_key = owner['person_key']
    owner_name = owner['name']
    
    if not person_key:
        print(f"   ⚠️  No PersonKey for {owner_name}")
        return
    
    print(f"\n      📞 Step 3a: Testing Phone API for {owner_name}")
    test_phone_api(person_key, owner_name, api_key)
    
    print(f"\n      📧 Step 3b: Testing Email API for {owner_name}")
    test_email_api(person_key, owner_name, api_key)

def test_phone_api(person_key, owner_name, api_key):
    """Test phone API and track response"""
    url = f"https://api.propertyradar.com/v1/persons/{person_key}/Phone"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    params = {"Purchase": 1}
    
    try:
        response = requests.post(url, headers=headers, params=params, timeout=30)
        print(f"      📡 Phone Response: {response.status_code}")
        
        if response.status_code == 200:
            phone_data = response.json()
            
            # Track costs and results
            total_cost = phone_data.get('totalCost', 0)
            result_count = phone_data.get('resultCount', 0)
            
            print(f"      💰 Phone API Cost: ${total_cost}")
            print(f"      📊 Phone Records: {result_count}")
            print(f"      ✅ PHONE API SUCCESS for {owner_name}")
            
            # Show actual phone data if available
            if 'results' in phone_data and phone_data['results']:
                print(f"      📞 Phone data found!")
                # Don't print actual phone numbers for privacy, just confirm we got them
                print(f"      📄 Response: {json.dumps(phone_data, indent=2)}")
            
            return phone_data
        else:
            print(f"      ❌ Phone API failed: {response.status_code}")
            print(f"      📄 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"      ❌ Phone API exception: {e}")
        return None

def test_email_api(person_key, owner_name, api_key):
    """Test email API and track response"""
    url = f"https://api.propertyradar.com/v1/persons/{person_key}/Email"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    params = {"Purchase": 1}
    
    try:
        response = requests.post(url, headers=headers, params=params, timeout=30)
        print(f"      📡 Email Response: {response.status_code}")
        
        if response.status_code == 200:
            email_data = response.json()
            
            # Track costs and results
            total_cost = email_data.get('totalCost', 0)
            result_count = email_data.get('resultCount', 0)
            
            print(f"      💰 Email API Cost: ${total_cost}")
            print(f"      📊 Email Records: {result_count}")
            print(f"      ✅ EMAIL API SUCCESS for {owner_name}")
            
            # Show actual email data if available
            if 'results' in email_data and email_data['results']:
                print(f"      📧 Email data found!")
                print(f"      📄 Response: {json.dumps(email_data, indent=2)}")
            
            return email_data
        else:
            print(f"      ❌ Email API failed: {response.status_code}")
            print(f"      📄 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"      ❌ Email API exception: {e}")
        return None

def main():
    """Systematic test of PropertyRadar API with both commercial and residential addresses"""
    
    api_key = "a1b7cec841201499fecdfcd9a7124217ed2d51ed"
    
    # Test addresses - mix of commercial and residential
    test_addresses = [
        # Commercial addresses from our data
        ("1521 S Frontage Rd, Columbus, Ms 39701", "COMMERCIAL"),
        ("1601 Highway 45 N, Columbus, Ms 39705", "COMMERCIAL"),
        
        # Residential addresses from our data  
        ("1555 Arrington Rd, College Station, Tx 77845", "RESIDENTIAL"),
        ("1701 Ragu Dr, Owensboro, Ky 42303", "RESIDENTIAL"),
        ("1713 E Bowman Dr, Greenville, Il 62246", "RESIDENTIAL"),
        
        # Known working address from your screenshot
        ("610 VIA RAVELLO APT 402, IRVING, TX 75039", "RESIDENTIAL - KNOWN WORKING"),
    ]
    
    print("🧪 SYSTEMATIC PROPERTYRADAR API TEST")
    print("=" * 80)
    print("📋 Testing both commercial and residential addresses")
    print("💰 Tracking all costs and charges")
    print("🔍 Monitoring what actually works vs fails")
    print("=" * 80)
    
    total_tests = len(test_addresses)
    successful_properties = 0
    successful_owners = 0
    successful_phones = 0
    successful_emails = 0
    
    for i, (address, category) in enumerate(test_addresses, 1):
        print(f"\n🎯 TEST {i}/{total_tests}: {category}")
        
        result = test_property_search(address, api_key)
        
        if result:
            successful_properties += 1
        
        # Rate limiting between tests
        if i < total_tests:
            print(f"\n⏳ Waiting 3 seconds before next test...")
            time.sleep(3)
    
    print("\n" + "=" * 80)
    print("📊 SYSTEMATIC TEST RESULTS")
    print("=" * 80)
    print(f"✅ Successful Property Searches: {successful_properties}/{total_tests}")
    print(f"💡 This systematic approach will help us:")
    print(f"   - Track exact costs for each API call")
    print(f"   - Identify which address types work best")
    print(f"   - See the real vs expected API behavior")
    print(f"   - Reverse engineer the working process")

if __name__ == "__main__":
    main() 