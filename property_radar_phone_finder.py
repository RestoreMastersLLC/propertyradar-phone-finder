#!/usr/bin/env python3
"""
Property Radar Phone Finder

This script follows the correct PropertyRadar API flow:
1. Search for properties by address using Properties API  
2. Extract owner information from property data
3. Get phone numbers for owners using Persons API

Based on PropertyRadar API documentation:
- Properties: https://developers.propertyradar.com/#tag/Properties
- Persons: https://developers.propertyradar.com/#tag/Persons  
- Phone: https://developers.propertyradar.com/#operation/POST/persons/PersonKey/Phone
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

class PropertyRadarPhoneFinder:
    def __init__(self, monday_token: str, property_radar_token: str):
        self.monday_token = monday_token
        self.property_radar_token = property_radar_token
        
        # Monday.com API setup
        self.monday_url = "https://api.monday.com/v2"
        self.monday_headers = {
            "Authorization": f"Bearer {monday_token}",
            "Content-Type": "application/json"
        }
        
        # Property Radar API setup
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

    def search_properties_by_address(self, address: str) -> Optional[Dict]:
        """Step 1: Search for properties using PropertyRadar Properties API"""
        print(f"🔍 Step 1: Searching properties for address: {address}")
        
        try:
            # PropertyRadar API requires Purchase parameter - try with Purchase=1
            search_data = {
                "Purchase": 1,  # API requires this - will charge for results
                "Criteria": [
                    {
                        "Name": "Address",
                        "Value": [address]
                    }
                ]
            }
            
            print(f"📤 Sending request: {json.dumps(search_data, indent=2)}")
            
            # Try the postProperties endpoint mentioned in documentation
            response = requests.post(f"{self.radar_url}/postProperties", 
                                   headers=self.radar_headers, 
                                   json=search_data, 
                                   timeout=30)
            
            print(f"📡 Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Found property data")
                
                # Show response structure for debugging
                if 'Properties' in data and data['Properties']:
                    print(f"📊 Found {len(data['Properties'])} properties")
                    return data
                elif 'properties' in data and data['properties']:
                    print(f"📊 Found {len(data['properties'])} properties")  
                    return data
                else:
                    print(f"⚠️  No properties found in response")
                    print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    return None
            else:
                print(f"❌ Method 1 failed: {response.status_code}")
                print(f"Error details: {response.text}")
                
                # Try alternative approaches
                return self.try_alternative_property_search(address)
                
        except Exception as e:
            print(f"❌ Error searching properties: {e}")
            return None

    def try_alternative_property_search(self, address: str) -> Optional[Dict]:
        """Try alternative property search methods"""
        print(f"🔄 Trying alternative property search methods...")
        
        # Method 2: Try with Purchase=0 (test mode)
        try:
            search_data_v2 = {
                "Purchase": 0,  # Test mode
                "Criteria": [
                    {
                        "Name": "Address",
                        "Value": [address]
                    }
                ]
            }
            
            print(f"📤 Method 2: {json.dumps(search_data_v2, indent=2)}")
            
            response = requests.post(f"{self.radar_url}/postProperties", 
                                   headers=self.radar_headers, 
                                   json=search_data_v2, 
                                   timeout=30)
            
            print(f"📡 Method 2 Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Method 2 succeeded!")
                return data
                
        except Exception as e:
            print(f"⚠️  Method 2 error: {e}")
        
        # Method 3: Try with SiteAddress instead of Address
        try:
            search_data_v3 = {
                "Criteria": [
                    {
                        "Name": "SiteAddress",  # Try SiteAddress
                        "Value": [address]
                    }
                ]
            }
            
            print(f"📤 Method 3: {json.dumps(search_data_v3, indent=2)}")
            
            response = requests.post(f"{self.radar_url}/postProperties", 
                                   headers=self.radar_headers, 
                                   json=search_data_v3, 
                                   timeout=30)
            
            print(f"📡 Method 3 Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Method 3 succeeded!")
                return data
                
        except Exception as e:
            print(f"⚠️  Method 3 error: {e}")
        
        # Method 4: Try GET with query parameters
        try:
            print(f"📤 Method 4: GET with query parameters")
            
            params = {"address": address}
            response = requests.get(f"{self.radar_url}/postProperties", 
                                  headers=self.radar_headers, 
                                  params=params, 
                                  timeout=30)
            
            print(f"📡 Method 4 Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Method 4 succeeded!")
                return data
                
        except Exception as e:
            print(f"⚠️  Method 4 error: {e}")
        
        print(f"❌ All property search methods failed for: {address}")
        return None

    def extract_owner_info(self, property_data: Dict) -> List[Dict]:
        """Step 2: Extract owner information from property data"""
        print(f"🔍 Step 2: Extracting owner information")
        
        owners = []
        
        # Check different possible data structures
        properties = property_data.get('Properties', property_data.get('properties', []))
        
        if not properties:
            print(f"⚠️  No properties found in data")
            return owners
        
        for prop in properties:
            if not isinstance(prop, dict):
                continue
                
            print(f"📋 Processing property: {prop.get('Address', 'Unknown address')}")
            
            # Look for owner information in various fields
            owner_fields_to_check = [
                'Owner', 'Owners', 'owner', 'owners',
                'OwnerName', 'owner_name', 'PropertyOwner'
            ]
            
            for field in owner_fields_to_check:
                if field in prop and prop[field]:
                    owner_data = prop[field]
                    
                    if isinstance(owner_data, list):
                        for owner in owner_data:
                            if isinstance(owner, dict):
                                owners.append(owner)
                    elif isinstance(owner_data, dict):
                        owners.append(owner_data)
                    elif isinstance(owner_data, str):
                        # If it's just a string name, create a minimal owner object
                        owners.append({"Name": owner_data})
            
            # Also check for PersonKey or similar identifiers that we can use for phone lookup
            person_key_fields = ['PersonKey', 'person_key', 'OwnerKey', 'owner_key']
            for field in person_key_fields:
                if field in prop and prop[field]:
                    # Add person key to existing owners or create new entry
                    if owners:
                        owners[-1][field] = prop[field]
                    else:
                        owners.append({field: prop[field]})
        
        print(f"✅ Found {len(owners)} owner(s)")
        for i, owner in enumerate(owners, 1):
            owner_name = owner.get('Name', owner.get('OwnerName', f"Owner {i}"))
            print(f"   👤 {owner_name}")
        
        return owners

    def get_owner_phones(self, owner_info: Dict) -> List[str]:
        """Step 3: Get phone numbers for owner using Persons API"""
        print(f"🔍 Step 3: Getting phone numbers for owner")
        
        phones = []
        
        # Look for PersonKey or similar identifier
        person_key = None
        key_fields = ['PersonKey', 'person_key', 'OwnerKey', 'owner_key', 'Key', 'ID']
        
        for field in key_fields:
            if field in owner_info and owner_info[field]:
                person_key = owner_info[field]
                break
        
        if not person_key:
            print(f"⚠️  No PersonKey found for owner")
            return phones
        
        print(f"📞 Using PersonKey: {person_key}")
        
        try:
            # Use the PropertyRadar Persons API to get phone numbers
            # Based on documentation: POST /v1/persons/{PersonKey}/phone
            phone_url = f"{self.radar_url}/persons/{person_key}/phone"
            
            # The API might require a Purchase parameter
            phone_data = {
                "Purchase": 0  # Test mode first
            }
            
            response = requests.post(phone_url, 
                                   headers=self.radar_headers, 
                                   json=phone_data, 
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
                # Handle other formats
                cleaned_phones.append(phone)
        
        return list(set(cleaned_phones))  # Remove duplicates

    def process_addresses(self, board_id: str, limit: int = 10):
        """Main processing function"""
        print("🚀 PropertyRadar Phone Finder")
        print("=" * 60)
        print("Following API flow: Properties → Owners → Phone Numbers")
        print("=" * 60)
        
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
            
            # Step 1: Search for properties
            property_data = self.search_properties_by_address(address)
            
            if not property_data:
                self.results.append({
                    "item_id": item.get('id'),
                    "address": address,
                    "owners": [],
                    "phones": [],
                    "status": "Property not found"
                })
                continue
            
            # Step 2: Extract owner information
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
            
            # Step 3: Get phone numbers for each owner
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
        print("📊 PROPERTY RADAR PHONE SEARCH RESULTS")
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
    
    # Create finder instance
    finder = PropertyRadarPhoneFinder(MONDAY_API_TOKEN, PROPERTY_RADAR_API_KEY)
    
    # Find phone numbers
    finder.process_addresses(BOARD_ID, limit=10)

if __name__ == "__main__":
    main() 