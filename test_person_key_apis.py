#!/usr/bin/env python3
"""
Test PropertyRadar Phone and Email APIs with known PersonKey
"""

import requests
import json

def test_phone_api(person_key, api_key):
    """Test phone API with known PersonKey"""
    print(f"📞 Testing Phone API for PersonKey: {person_key}")
    
    url = f"https://api.propertyradar.com/v1/persons/{person_key}/Phone"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    params = {"Purchase": 1}
    
    try:
        response = requests.post(url, headers=headers, params=params, timeout=30)
        
        print(f"📡 Phone API response: {response.status_code}")
        print(f"📄 Raw response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Phone API SUCCESS!")
            print(f"📄 Phone data: {json.dumps(data, indent=2)}")
            return data
        else:
            print(f"❌ Phone API error: {response.status_code}")
            print(f"Error details: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Phone API exception: {e}")
        return None

def test_email_api(person_key, api_key):
    """Test email API with known PersonKey"""
    print(f"\n📧 Testing Email API for PersonKey: {person_key}")
    
    url = f"https://api.propertyradar.com/v1/persons/{person_key}/Email"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    params = {"Purchase": 1}
    
    try:
        response = requests.post(url, headers=headers, params=params, timeout=30)
        
        print(f"📡 Email API response: {response.status_code}")
        print(f"📄 Raw response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Email API SUCCESS!")
            print(f"📄 Email data: {json.dumps(data, indent=2)}")
            return data
        else:
            print(f"❌ Email API error: {response.status_code}")
            print(f"Error details: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Email API exception: {e}")
        return None

def main():
    """Test both APIs with multiple PersonKeys"""
    
    api_key = "a1b7cec841201499fecdfcd9a7124217ed2d51ed"
    
    # Test multiple PersonKeys from our results
    test_cases = [
        ("p658049745", "ATMOS ENERGY CORP", "Corporate entity"),
        ("p921390959", "Unknown Owner", "Individual (College Station)"),
        ("p921390960", "HBJ STORAGE II LLC", "LLC entity"),
        ("p276205689", "Unknown Owner", "Individual (Mena, AR)"),
        ("p635239918", "POLK COUNTY FAIR & RODEO ASSOC", "Association"),
        ("p633980473", "LAYSAN BIO INC", "Corporation"),
        ("p922313828", "Unknown Owner", "Individual (Gainesville, FL)"),
    ]
    
    print(f"🧪 Testing PropertyRadar Phone/Email APIs with Multiple PersonKeys")
    print("=" * 70)
    
    successful_tests = []
    failed_tests = []
    
    for person_key, owner_name, entity_type in test_cases:
        print(f"\n👤 Testing PersonKey: {person_key}")
        print(f"🏢 Owner: {owner_name}")
        print(f"📋 Type: {entity_type}")
        print("-" * 50)
        
        # Test phone API
        phone_data = test_phone_api(person_key, api_key)
        
        # Test email API  
        email_data = test_email_api(person_key, api_key)
        
        if phone_data or email_data:
            successful_tests.append((person_key, owner_name, entity_type))
            print(f"✅ SUCCESS: Found contact data for {owner_name}")
        else:
            failed_tests.append((person_key, owner_name, entity_type))
            print(f"❌ FAILED: No contact data for {owner_name}")
    
    print("\n" + "=" * 70)
    print("🎯 FINAL TEST RESULTS:")
    print(f"✅ Successful: {len(successful_tests)}")
    print(f"❌ Failed: {len(failed_tests)}")
    
    if successful_tests:
        print(f"\n🎉 SUCCESS CASES:")
        for person_key, owner_name, entity_type in successful_tests:
            print(f"   {person_key}: {owner_name} ({entity_type})")
    
    if failed_tests:
        print(f"\n⚠️  FAILED CASES:")
        for person_key, owner_name, entity_type in failed_tests:
            print(f"   {person_key}: {owner_name} ({entity_type})")
    
    print(f"\n💡 INSIGHTS:")
    if len(successful_tests) > 0:
        print(f"   - The API sequence is working correctly")
        print(f"   - Some entities have available contact data")
    else:
        print(f"   - No contact data available for any of these entities")
        print(f"   - This could be due to:")
        print(f"     • Corporate entities don't have personal contact info")
        print(f"     • Data already purchased/used")
        print(f"     • No contact data available in PropertyRadar database")

if __name__ == "__main__":
    main() 