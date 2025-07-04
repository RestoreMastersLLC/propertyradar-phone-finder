#!/usr/bin/env python3
"""
Check Full PropertyRadar Response

Now that we have the working API format, let's examine the complete response
to understand the data structure and find owner information.
"""

import requests
import json
import re

def parse_address(full_address):
    """Parse full address into components"""
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

def check_full_response():
    test_address = "400 LAS COLINAS BLVD E, IRVING, TX 75039"
    api_key = "a1b7cec841201499fecdfcd9a7124217ed2d51ed"
    
    print(f"🔍 Checking full PropertyRadar response:")
    print(f"📍 Address: {test_address}")
    print(f"👤 Expected owner: NATHAN P PETROWSKY, 71")
    print()
    
    # Parse address into components
    components = parse_address(test_address)
    
    if not components:
        print(f"❌ Could not parse address")
        return False
    
    url = "https://api.propertyradar.com/v1/properties"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    params = {"Purchase": 1}  # Paid search
    
    # Use separate address components (working format)
    data = {
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
        response = requests.post(url, headers=headers, json=data, params=params, timeout=30)
        
        print(f"📡 Response: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            
            if 'results' in response_data and response_data['results']:
                results = response_data['results']
                print(f"✅ Found {len(results)} property result(s)")
                
                # Show FULL response for analysis
                print(f"\n📄 COMPLETE RESPONSE:")
                print("=" * 80)
                print(json.dumps(response_data, indent=2))
                print("=" * 80)
                
                # Analyze first result in detail
                if results:
                    first_result = results[0]
                    print(f"\n🔍 DETAILED ANALYSIS:")
                    print(f"Total fields: {len(first_result)}")
                    
                    # Categorize fields
                    location_fields = []
                    property_fields = []
                    financial_fields = []
                    status_fields = []
                    owner_fields = []
                    other_fields = []
                    
                    for key, value in first_result.items():
                        key_lower = key.lower()
                        if any(x in key_lower for x in ['owner', 'person', 'name']):
                            owner_fields.append((key, value))
                        elif any(x in key_lower for x in ['lat', 'long', 'address', 'city', 'state', 'zip']):
                            location_fields.append((key, value))
                        elif any(x in key_lower for x in ['sqft', 'lot', 'year', 'type', 'property']):
                            property_fields.append((key, value))
                        elif any(x in key_lower for x in ['value', 'loan', 'transfer', 'assessed']):
                            financial_fields.append((key, value))
                        elif key.startswith('is') or key.startswith('in') or key.startswith('has'):
                            status_fields.append((key, value))
                        else:
                            other_fields.append((key, value))
                    
                    print(f"\n📍 LOCATION FIELDS ({len(location_fields)}):")
                    for key, value in location_fields:
                        print(f"   {key}: {value}")
                    
                    print(f"\n🏠 PROPERTY FIELDS ({len(property_fields)}):")
                    for key, value in property_fields:
                        print(f"   {key}: {value}")
                    
                    print(f"\n💰 FINANCIAL FIELDS ({len(financial_fields)}):")
                    for key, value in financial_fields:
                        print(f"   {key}: {value}")
                    
                    print(f"\n👤 OWNER-RELATED FIELDS ({len(owner_fields)}):")
                    if owner_fields:
                        for key, value in owner_fields:
                            print(f"   {key}: {value}")
                    else:
                        print("   ⚠️  No obvious owner fields found!")
                        print("   📋 This suggests owner data might be in a separate API call")
                    
                    print(f"\n🏷️  STATUS FIELDS ({len(status_fields)}):")
                    for key, value in status_fields:
                        if value:  # Only show True values
                            print(f"   {key}: {value}")
                    
                    print(f"\n🔧 OTHER FIELDS ({len(other_fields)}):")
                    for key, value in other_fields:
                        print(f"   {key}: {value}")
                    
                    # Look for any field that might contain owner info
                    print(f"\n🔍 SEARCHING FOR HIDDEN OWNER INFO:")
                    for key, value in first_result.items():
                        if isinstance(value, (dict, list)) and value:
                            print(f"   Complex field '{key}': {type(value)} - {str(value)[:100]}...")
                        elif isinstance(value, str) and any(name_part in value.upper() for name_part in ['NATHAN', 'PETROWSKY', 'CANAL']):
                            print(f"   🎯 Potential owner data in '{key}': {value}")
                
                return True
            else:
                print(f"⚠️  No results found")
                print(f"Response: {json.dumps(response_data, indent=2)}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Details: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False
    
    return False

if __name__ == "__main__":
    check_full_response() 