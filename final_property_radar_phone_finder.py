#!/usr/bin/env python3
"""
✅ WORKING PropertyRadar Phone Finder

This script uses the correct PropertyRadar API format:
- Purchase parameter in query string
- Lowercase "name" and "value" in Criteria
- Proper authentication with Bearer token

⚠️  WARNING: This will charge your PropertyRadar account for each property search!
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

class WorkingPropertyRadarPhoneFinder:
    def __init__(self, monday_token: str, property_radar_token: str):
        self.monday_token = monday_token
        self.property_radar_token = property_radar_token
        
        # Monday.com API setup
        self.monday_url = "https://api.monday.com/v2"
        self.monday_headers = {
            "Authorization": f"Bearer {monday_token}",
            "Content-Type": "application/json"
        }
        
        # Property Radar API setup (WORKING FORMAT!)
        self.radar_url = "https://api.propertyradar.com/v1"
        self.radar_headers = {
            "Authorization": f"Bearer {property_radar_token}",
            "Content-Type": "application/json",
            "User-Agent": "PropertyRadar-Phone-Finder/1.0"
        }
        
        self.results = []

    def get_monday_addresses(self, board_id: str, limit: int = 10) -> List[Dict]:
        """Get addresses from Monday.com board"""
        print(f"📋 Getting addresses from Monday.com board {board_id}...")
        
        query = """
        query ($board_id: [ID!], $limit: Int) {
            boards(ids: $board_id) {
                name
                items_page(limit: $limit) {
                    items {
                        id
                        name
                        column_values {
                            id
                            text
                            value
                        }
                    }
                }
            }
        }
        """
        
        variables = {"board_id": [board_id], "limit": limit}
        payload = {"query": query, "variables": variables}
        
        try:
            response = requests.post(self.monday_url, headers=self.monday_headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data', {}).get('boards'):
                    board = data['data']['boards'][0]
                    items = board['items_page']['items']
                    print(f"✅ Found {len(items)} items")
                    return items
            
            print(f"❌ Error getting Monday.com data: {response.status_code}")
            return []
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return []

    def extract_address(self, item: Dict) -> Optional[str]:
        """Extract address from Monday.com item"""
        item_name = item.get('name', '')
        
        # Skip "New address" entries
        if item_name == 'New address':
            return None
            
        # Check if the item name looks like an address
        address_indicators = ['st', 'rd', 'ave', 'blvd', 'ln', 'dr', 'way', 'ct', 'pl']
        if any(indicator in item_name.lower() for indicator in address_indicators):
            return item_name
        
        # Check column values for address data
        for column in item.get('column_values', []):
            if column.get('text'):
                text = column['text']
                if any(indicator in text.lower() for indicator in address_indicators):
                    return text
        
        return item_name if item_name else None

    def search_properties_by_address(self, address: str, use_paid_search: bool = False) -> Optional[Dict]:
        """Search for properties using the WORKING PropertyRadar Properties API format"""
        print(f"🔍 Searching properties for address: {address}")
        
        try:
            # ✅ WORKING PropertyRadar API format:
            # - Purchase parameter in query string
            # - Lowercase "name" and "value" in Criteria
            
            # Query parameters (Purchase goes here, not in body!)
            params = {
                "Purchase": 1 if use_paid_search else 0
            }
            
            # Request body with LOWERCASE field names
            request_data = {
                "Criteria": [
                    {
                        "name": "Address",    # lowercase "name"
                        "value": [address]    # lowercase "value"
                    }
                ]
            }
            
            if use_paid_search:
                print(f"💰 WARNING: Using Purchase=1 - This will charge your account!")
            else:
                print(f"🆓 Using Purchase=0 - Test mode (may not return results)")
            
            print(f"📤 Query params: {params}")
            print(f"📤 Request body: {json.dumps(request_data, indent=2)}")
            
            response = requests.post(f"{self.radar_url}/properties", 
                                   headers=self.radar_headers, 
                                   json=request_data,
                                   params=params,
                                   timeout=30)
            
            print(f"📡 Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ PropertyRadar API call successful!")
                
                # Check for results
                if 'results' in data:
                    results = data['results']
                    print(f"📊 Found {len(results)} property result(s)")
                    
                    if results:
                        return data
                    else:
                        if not use_paid_search:
                            print(f"⚠️  No results in test mode. Try with paid search for real data.")
                        else:
                            print(f"⚠️  No properties found for this address")
                        return None
                else:
                    print(f"⚠️  No 'results' key in response")
                    return None
            else:
                print(f"❌ PropertyRadar API error: {response.status_code}")
                print(f"Error details: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error searching properties: {e}")
            return None

    def extract_owner_info(self, property_data: Dict) -> List[Dict]:
        """Extract owner information from PropertyRadar property data"""
        print(f"🔍 Extracting owner information from PropertyRadar response")
        
        owners = []
        
        if 'results' not in property_data:
            print(f"⚠️  No results in property data")
            return owners
        
        results = property_data['results']
        
        for result in results:
            if not isinstance(result, dict):
                continue
                
            print(f"📋 Processing property result")
            print(f"Property keys: {list(result.keys())}")
            
            # Look for owner information in various possible fields
            owner_fields_to_check = [
                'Owner', 'owner', 'OwnerName', 'owner_name', 
                'PropertyOwner', 'property_owner', 'Name', 'name'
            ]
            
            found_owner = False
            for field in owner_fields_to_check:
                if field in result and result[field]:
                    owner_data = result[field]
                    print(f"👤 Found owner field '{field}': {owner_data}")
                    
                    if isinstance(owner_data, list):
                        for owner in owner_data:
                            if isinstance(owner, dict):
                                owners.append(owner)
                            else:
                                owners.append({"Name": str(owner)})
                    elif isinstance(owner_data, dict):
                        owners.append(owner_data)
                    elif isinstance(owner_data, str):
                        owners.append({"Name": owner_data})
                    
                    found_owner = True
                    break
            
            # Look for PersonKey or similar identifiers for phone lookup
            person_key_fields = ['PersonKey', 'person_key', 'OwnerKey', 'owner_key', 'Key', 'ID', 'Id']
            for field in person_key_fields:
                if field in result and result[field]:
                    print(f"🔑 Found person key field '{field}': {result[field]}")
                    # Add person key to existing owners or create new entry
                    if owners:
                        owners[-1][field] = result[field]
                    else:
                        owners.append({field: result[field]})
            
            if not found_owner:
                print(f"⚠️  No standard owner fields found. All fields: {list(result.keys())}")
        
        print(f"✅ Found {len(owners)} owner record(s)")
        return owners

    def get_owner_phones(self, owner_info: Dict) -> List[str]:
        """Get phone numbers for owner using PropertyRadar Persons API"""
        print(f"🔍 Getting phone numbers for owner: {owner_info.get('Name', 'Unknown')}")
        
        phones = []
        
        # Look for PersonKey or similar identifier
        person_key = None
        key_fields = ['PersonKey', 'person_key', 'OwnerKey', 'owner_key', 'Key', 'ID', 'Id']
        
        for field in key_fields:
            if field in owner_info and owner_info[field]:
                person_key = owner_info[field]
                print(f"📞 Using {field}: {person_key}")
                break
        
        if not person_key:
            print(f"⚠️  No PersonKey found for owner - cannot get phone numbers")
            return phones
        
        try:
            # Use the PropertyRadar Persons API to get phone numbers
            # Based on documentation: POST /v1/persons/{PersonKey}/phone
            phone_url = f"{self.radar_url}/persons/{person_key}/phone"
            
            # The phone API might also require Purchase parameter
            phone_params = {"Purchase": 1}  # Will charge for phone numbers
            
            print(f"💰 WARNING: Phone lookup will charge your account!")
            
            response = requests.post(phone_url, 
                                   headers=self.radar_headers, 
                                   params=phone_params, 
                                   timeout=30)
            
            print(f"📡 Phone API response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract phone numbers from response
                phone_numbers = self.extract_phones_from_response(data)
                phones.extend(phone_numbers)
                
                if phone_numbers:
                    print(f"✅ Found {len(phone_numbers)} phone number(s)")
                    for phone in phone_numbers:
                        print(f"   📞 {phone}")
                else:
                    print(f"⚠️  No phone numbers in response")
                    
            else:
                print(f"❌ Phone API error: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error getting phone numbers: {e}")
        
        return phones

    def extract_phones_from_response(self, data: Dict) -> List[str]:
        """Extract and format phone numbers from API response"""
        phones = []
        
        def find_phones_recursive(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if 'phone' in key.lower() and value:
                        phones.append(str(value))
                    elif isinstance(value, (dict, list)):
                        find_phones_recursive(value, current_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    current_path = f"{path}[{i}]" if path else f"[{i}]"
                    find_phones_recursive(item, current_path)
        
        find_phones_recursive(data)
        
        # Clean and format phone numbers
        cleaned_phones = []
        for phone in phones:
            # Extract digits only
            digits = ''.join(c for c in str(phone) if c.isdigit())
            if len(digits) == 10:
                formatted = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
                cleaned_phones.append(formatted)
            elif len(digits) == 11 and digits.startswith('1'):
                formatted = f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
                cleaned_phones.append(formatted)
            elif len(digits) >= 10:
                cleaned_phones.append(phone)
        
        return list(set(cleaned_phones))  # Remove duplicates

    def process_addresses(self, board_id: str, limit: int = 10, use_paid_search: bool = False):
        """Main processing function"""
        print("🚀 PropertyRadar Phone Finder (WORKING VERSION)")
        print("=" * 60)
        print("✅ Using correct PropertyRadar API format:")
        print("   - Purchase parameter in query string")
        print("   - Lowercase 'name' and 'value' in Criteria")
        print("=" * 60)
        
        if use_paid_search:
            print("💰 WARNING: Using paid search mode - will charge your account!")
        else:
            print("🆓 Using test mode - may not return results")
        print()
        
        # Get addresses from Monday.com
        items = self.get_monday_addresses(board_id, limit)
        
        if not items:
            print("❌ No items found")
            return
        
        print(f"\n📋 Processing {len(items)} items...")
        print("=" * 60)
        
        for i, item in enumerate(items, 1):
            print(f"\n🏠 Item {i}/{len(items)}")
            print("-" * 40)
            
            address = self.extract_address(item)
            
            if not address:
                print("⚠️  No valid address found")
                self.results.append({
                    "item_id": item.get('id'),
                    "address": "No address",
                    "owners": [],
                    "phones": [],
                    "status": "No address"
                })
                continue
            
            print(f"📍 Address: {address}")
            
            # Search for properties
            property_data = self.search_properties_by_address(address, use_paid_search)
            
            if not property_data:
                self.results.append({
                    "item_id": item.get('id'),
                    "address": address,
                    "owners": [],
                    "phones": [],
                    "status": "Property not found"
                })
                continue
            
            # Extract owner information
            owners = self.extract_owner_info(property_data)
            
            if not owners:
                self.results.append({
                    "item_id": item.get('id'),
                    "address": address,
                    "owners": [],
                    "phones": [],
                    "status": "No owners found"
                })
                continue
            
            # Get phone numbers for each owner
            all_phones = []
            owner_details = []
            
            for owner in owners:
                owner_name = owner.get('Name', owner.get('OwnerName', 'Unknown'))
                owner_phones = self.get_owner_phones(owner)
                
                owner_details.append({
                    "name": owner_name,
                    "phones": owner_phones
                })
                
                all_phones.extend(owner_phones)
            
            # Store results
            result = {
                "item_id": item.get('id'),
                "address": address,
                "owners": owner_details,
                "phones": list(set(all_phones)),  # Remove duplicates
                "status": "Success" if all_phones else "No phones found"
            }
            self.results.append(result)
            
            if all_phones:
                print(f"🎉 Found {len(set(all_phones))} unique phone number(s) for {address}")
                for phone in set(all_phones):
                    print(f"   📞 {phone}")
            else:
                print(f"📞 No phone numbers found for {address}")
            
            # Rate limiting
            time.sleep(2)
        
        self.generate_report()

    def generate_report(self):
        """Generate final report"""
        print("\n" + "=" * 60)
        print("📊 PROPERTYRADAR PHONE SEARCH RESULTS")
        print("=" * 60)
        
        total_addresses = len(self.results)
        addresses_with_phones = sum(1 for r in self.results if r['phones'])
        total_phones = sum(len(r['phones']) for r in self.results)
        
        print(f"\n📈 SUMMARY:")
        print(f"   Total Addresses Processed: {total_addresses}")
        print(f"   Addresses with Phone Numbers: {addresses_with_phones}")
        print(f"   Total Unique Phone Numbers: {total_phones}")
        
        print(f"\n📋 DETAILED RESULTS:")
        for i, result in enumerate(self.results, 1):
            print(f"\n{i}. {result['address']}")
            print(f"   Status: {result['status']}")
            
            if result['owners']:
                print(f"   Owners:")
                for owner in result['owners']:
                    print(f"     👤 {owner['name']}")
                    for phone in owner['phones']:
                        print(f"       📞 {phone}")
            
            if result['phones']:
                print(f"   All Phone Numbers:")
                for phone in result['phones']:
                    print(f"     📞 {phone}")
        
        # Save results
        try:
            with open("propertyradar_phone_results.json", "w") as f:
                json.dump(self.results, f, indent=2)
            print(f"\n💾 Results saved to: propertyradar_phone_results.json")
        except Exception as e:
            print(f"\n⚠️  Could not save results: {e}")

def main():
    # API credentials
    MONDAY_API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjMxOTcyMjAwMywiYWFpIjoxMSwidWlkIjo1NDE1NDI4MSwiaWFkIjoiMjAyNC0wMi0wOVQyMzowODo0Ni4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MTI4NDMxMTksInJnbiI6InVzZTEifQ.xshH7gVvlzc89H7bePImbYudk58FLS9vmr6NggMhxeY"
    PROPERTY_RADAR_API_KEY = "a1b7cec841201499fecdfcd9a7124217ed2d51ed"
    BOARD_ID = "9009448650"
    
    print("🚀 PropertyRadar Phone Finder")
    print("=" * 40)
    print("Choose search mode:")
    print("1. Test mode (Purchase=0) - Free but may not return results")
    print("2. Paid mode (Purchase=1) - Real results but charges your account")
    print()
    
    # For now, default to test mode to avoid charges
    # User can modify this to use paid mode
    USE_PAID_SEARCH = False  # Set to True for real results (charges account)
    
    if USE_PAID_SEARCH:
        print("💰 USING PAID MODE - Will charge your PropertyRadar account!")
    else:
        print("🆓 USING TEST MODE - May not return results")
    
    print()
    
    # Create finder instance
    finder = WorkingPropertyRadarPhoneFinder(MONDAY_API_TOKEN, PROPERTY_RADAR_API_KEY)
    
    # Find phone numbers
    finder.process_addresses(BOARD_ID, limit=10, use_paid_search=USE_PAID_SEARCH)

if __name__ == "__main__":
    main() 