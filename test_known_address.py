#!/usr/bin/env python3
"""
Test PropertyRadar API with Known Working Address

Testing with: 400 LAS COLINAS BLVD E, IRVING, TX 75039
(From user's screenshot showing owner: NATHAN P PETROWSKY, 71)
"""

import requests
import json

def test_known_address():
    # Known working address from user's screenshot
    test_address = "400 LAS COLINAS BLVD E, IRVING, TX 75039"
    api_key = "a1b7cec841201499fecdfcd9a7124217ed2d51ed"
    
    print(f"🔍 Testing PropertyRadar with known working address:")
    print(f"📍 Address: {test_address}")
    print(f"👤 Expected owner: NATHAN P PETROWSKY, 71")
    print(f"📞 Expected phones: 510-541-7382, 925-552-5886, 925-376-5886")
    print()
    
    # Use the working PropertyRadar API format
    url = "https://api.propertyradar.com/v1/properties"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    params = {"Purchase": 1}  # Paid search
    data = {
        "Criteria": [
            {
                "name": "SiteAddress",  # Use SiteAddress for full addresses
                "value": [test_address]
            }
        ]
    }
    
    print(f"💰 Making paid PropertyRadar API call...")
    
    try:
        response = requests.post(url, headers=headers, json=data, params=params, timeout=30)
        
        print(f"📡 Response: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            
            print(f"✅ API call successful!")
            
            if 'results' in response_data and response_data['results']:
                results = response_data['results']
                print(f"📊 Found {len(results)} property result(s)")
                
                # Show full response for analysis
                print(f"\n📄 Full response:")
                print(json.dumps(response_data, indent=2))
                
                # Analyze first result
                if results:
                    first_result = results[0]
                    print(f"\n🔍 First result analysis:")
                    print(f"Available keys: {list(first_result.keys())}")
                    
                    # Look for owner information
                    owner_fields = ['Owner', 'owner', 'OwnerName', 'owner_name', 'Name', 'name']
                    for field in owner_fields:
                        if field in first_result:
                            print(f"👤 {field}: {first_result[field]}")
                    
                    # Look for person keys
                    key_fields = ['PersonKey', 'person_key', 'OwnerKey', 'owner_key']
                    for field in key_fields:
                        if field in first_result:
                            print(f"🔑 {field}: {first_result[field]}")
                            
                            # If we find a PersonKey, try to get phone numbers
                            person_key = first_result[field]
                            print(f"\n📞 Attempting to get phone numbers...")
                            get_phone_numbers(person_key, api_key)
                
                return True
            else:
                print(f"⚠️  No results found even for known working address!")
                print(f"Response: {json.dumps(response_data, indent=2)}")
                return False
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def get_phone_numbers(person_key, api_key):
    """Get phone numbers using PropertyRadar Persons API"""
    print(f"📞 Getting phone numbers for PersonKey: {person_key}")
    
    url = f"https://api.propertyradar.com/v1/persons/{person_key}/phone"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    params = {"Purchase": 1}  # Paid phone lookup
    
    try:
        response = requests.post(url, headers=headers, params=params, timeout=30)
        
        print(f"📡 Phone API response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Phone API successful!")
            print(f"📄 Phone response:")
            print(json.dumps(data, indent=2))
            
            # Extract phone numbers
            phones = extract_phones_from_data(data)
            if phones:
                print(f"📞 Found phone numbers:")
                for phone in phones:
                    print(f"   📞 {phone}")
            else:
                print(f"⚠️  No phone numbers extracted from response")
        else:
            print(f"❌ Phone API error: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting phone numbers: {e}")

def extract_phones_from_data(data):
    """Extract phone numbers from API response"""
    phones = []
    
    def find_phones_recursive(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if 'phone' in key.lower() and value:
                    phones.append(str(value))
                elif isinstance(value, (dict, list)):
                    find_phones_recursive(value)
        elif isinstance(obj, list):
            for item in obj:
                find_phones_recursive(item)
    
    find_phones_recursive(data)
    
    # Clean and format phone numbers
    cleaned_phones = []
    for phone in phones:
        digits = ''.join(c for c in str(phone) if c.isdigit())
        if len(digits) == 10:
            formatted = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
            cleaned_phones.append(formatted)
        elif len(digits) == 11 and digits.startswith('1'):
            formatted = f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
            cleaned_phones.append(formatted)
        elif len(digits) >= 10:
            cleaned_phones.append(phone)
    
    return list(set(cleaned_phones))

if __name__ == "__main__":
    test_known_address() 