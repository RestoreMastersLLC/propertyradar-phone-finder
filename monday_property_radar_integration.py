#!/usr/bin/env python3
"""
Monday.com + Property Radar Integration Script

This script fetches addresses from a Monday.com board and uses Property Radar API
to find owner phone numbers for each property.

Board ID: 9009448650
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

class MondayPropertyRadarIntegration:
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
            "User-Agent": "Monday-PropertyRadar-Integration/1.0"
        }
        
        self.results = []

    def get_monday_board_items(self, board_id: str, limit: int = 10) -> List[Dict]:
        """Fetch items from Monday.com board"""
        print(f"🔍 Fetching first {limit} items from Monday board {board_id}...")
        
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
        
        variables = {
            "board_id": [board_id],
            "limit": limit
        }
        
        payload = {
            "query": query,
            "variables": variables
        }
        
        try:
            response = requests.post(self.monday_url, headers=self.monday_headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'errors' in data:
                    print(f"❌ Monday.com API errors: {data['errors']}")
                    return []
                
                if data.get('data', {}).get('boards'):
                    board = data['data']['boards'][0]
                    items = board['items_page']['items']
                    print(f"✅ Successfully fetched {len(items)} items from board '{board['name']}'")
                    return items
                else:
                    print("❌ No board data found")
                    return []
            else:
                print(f"❌ Monday.com API error: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error connecting to Monday.com: {e}")
            return []

    def extract_address_from_item(self, item: Dict) -> Optional[str]:
        """Extract address from Monday.com item"""
        # The address might be in the item name or in a specific column
        item_name = item.get('name', '')
        
        # Check if the item name looks like an address
        if any(indicator in item_name.lower() for indicator in ['st', 'rd', 'ave', 'blvd', 'ln', 'dr', 'way']):
            return item_name
        
        # Also check column values for address data
        for column in item.get('column_values', []):
            if column.get('text') and any(indicator in column['text'].lower() for indicator in ['st', 'rd', 'ave', 'blvd', 'ln', 'dr', 'way']):
                return column['text']
        
        return item_name if item_name != 'New address' else None

    def search_property_radar(self, address: str) -> Optional[Dict]:
        """Search Property Radar for property information and owner phone"""
        print(f"🔍 Searching Property Radar for: {address}")
        
        try:
            # Use the correct Property Radar API format based on documentation
            request_data = {
                "Purchase": 0,  # Test mode - no charges (capital 'Purchase')
                "Criteria": [   # capital 'Criteria'
                    {
                        "Name": "SiteAddress",  # Use SiteAddress for full address searches
                        "Value": [address]
                    }
                ]
            }
            
            print(f"🔍 Sending request: {json.dumps(request_data, indent=2)}")
            
            response = requests.post(f"{self.radar_url}/properties", 
                                   headers=self.radar_headers, 
                                   json=request_data, 
                                   timeout=30)
            
            print(f"📡 Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Found property data for {address}")
                print(f"📊 Response preview: {json.dumps(data, indent=2)[:500]}...")
                return data
            else:
                print(f"⚠️  Property Radar returned HTTP {response.status_code} for {address}")
                print(f"Error response: {response.text}")
                
                # Try alternative approaches
                if response.status_code == 400:
                    return self.search_property_radar_alternative(address)
                
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error searching Property Radar for {address}: {e}")
            return None

    def search_property_radar_alternative(self, address: str) -> Optional[Dict]:
        """Alternative Property Radar search method"""
        print(f"🔄 Trying alternative search for: {address}")
        
        try:
            # Try with Address instead of SiteAddress
            search_data = {
                "Purchase": 0,
                "Criteria": [
                    {
                        "Name": "Address", 
                        "Value": [address]
                    }
                ]
            }
            
            response = requests.post(f"{self.radar_url}/properties", 
                                   headers=self.radar_headers, 
                                   json=search_data, 
                                   timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Found property data (alternative method) for {address}")
                return data
            else:
                print(f"⚠️  Alternative search also failed for {address}: HTTP {response.status_code}")
                print(f"Error response: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Alternative search error for {address}: {e}")
            return None

    def extract_phone_from_property_data(self, property_data: Dict, address: str) -> List[str]:
        """Extract phone numbers from Property Radar response"""
        phones = []
        
        if not property_data:
            return phones
        
        print(f"🔍 Extracting phone data from response for {address}")
        
        # Check various possible locations for phone data
        locations_to_check = [
            property_data.get('properties', []),
            property_data.get('Properties', []),
            property_data.get('data', {}).get('properties', []),
            [property_data] if isinstance(property_data, dict) and ('owner' in property_data or 'owners' in property_data) else []
        ]
        
        for location in locations_to_check:
            if isinstance(location, list):
                for prop in location:
                    phones.extend(self.extract_phones_from_property(prop))
            elif isinstance(location, dict):
                phones.extend(self.extract_phones_from_property(location))
        
        # Remove duplicates and clean phone numbers
        unique_phones = list(set(phones))
        cleaned_phones = []
        
        for phone in unique_phones:
            # Clean phone number - remove non-digit characters
            cleaned = ''.join(c for c in str(phone) if c.isdigit())
            if len(cleaned) == 10:  # US phone number
                formatted = f"({cleaned[:3]}) {cleaned[3:6]}-{cleaned[6:]}"
                cleaned_phones.append(formatted)
            elif len(cleaned) == 11 and cleaned.startswith('1'):  # US phone with country code
                formatted = f"({cleaned[1:4]}) {cleaned[4:7]}-{cleaned[7:]}"
                cleaned_phones.append(formatted)
        
        return cleaned_phones

    def extract_phones_from_property(self, prop: Dict) -> List[str]:
        """Extract phone numbers from a single property object"""
        phones = []
        
        if not isinstance(prop, dict):
            return phones
        
        # Check owner information
        owner = prop.get('owner', {})
        if isinstance(owner, dict):
            for field in ['phone', 'mobile', 'phone_number', 'home_phone', 'work_phone']:
                if owner.get(field):
                    phones.append(owner[field])
        
        # Check direct phone fields
        for field in ['phone', 'owner_phone', 'contact_phone', 'mobile', 'phone_number']:
            if prop.get(field):
                phones.append(prop[field])
        
        # Check nested owner data
        if 'owners' in prop and isinstance(prop['owners'], list):
            for owner in prop['owners']:
                if isinstance(owner, dict):
                    for phone_field in ['phone', 'mobile', 'phone_number', 'home_phone', 'work_phone']:
                        if owner.get(phone_field):
                            phones.append(owner[phone_field])
        
        return phones

    def process_addresses(self, board_id: str, limit: int = 10):
        """Main processing function"""
        print("🚀 Starting Monday.com + Property Radar Integration")
        print("=" * 60)
        
        # Step 1: Get addresses from Monday.com
        items = self.get_monday_board_items(board_id, limit)
        
        if not items:
            print("❌ No items found in Monday.com board")
            return
        
        print(f"\n📋 Processing {len(items)} addresses...")
        print("=" * 60)
        
        # Step 2: Process each address
        for i, item in enumerate(items, 1):
            print(f"\n🏠 Item {i}/{len(items)}")
            print("-" * 40)
            
            # Extract address
            address = self.extract_address_from_item(item)
            
            if not address:
                print("⚠️  No valid address found in item")
                self.results.append({
                    "item_id": item.get('id'),
                    "address": "No address found",
                    "phones": [],
                    "status": "No address"
                })
                continue
            
            print(f"📍 Address: {address}")
            
            # Search Property Radar
            property_data = self.search_property_radar(address)
            
            # Extract phone numbers
            phones = self.extract_phone_from_property_data(property_data, address)
            
            if phones:
                print(f"📞 Found {len(phones)} phone number(s): {', '.join(phones)}")
                status = "Success"
            else:
                print("📞 No phone numbers found")
                status = "No phones found"
            
            # Store results
            result = {
                "item_id": item.get('id'),
                "address": address,
                "phones": phones,
                "status": status,
                "property_data": property_data is not None
            }
            self.results.append(result)
            
            # Add delay to respect rate limits
            time.sleep(2)  # Increased delay to be more respectful
        
        # Generate final report
        self.generate_report()

    def generate_report(self):
        """Generate final report"""
        print("\n" + "=" * 60)
        print("📊 FINAL REPORT - Phone Numbers Found")
        print("=" * 60)
        
        total_processed = len(self.results)
        successful_searches = sum(1 for r in self.results if r['property_data'])
        phones_found = sum(1 for r in self.results if r['phones'])
        total_phones = sum(len(r['phones']) for r in self.results)
        
        print(f"\n📈 SUMMARY:")
        print(f"   Total Addresses Processed: {total_processed}")
        print(f"   Successful Property Searches: {successful_searches}")
        print(f"   Addresses with Phone Numbers: {phones_found}")
        print(f"   Total Phone Numbers Found: {total_phones}")
        
        print(f"\n📋 DETAILED RESULTS:")
        for i, result in enumerate(self.results, 1):
            print(f"\n{i}. {result['address']}")
            if result['phones']:
                for phone in result['phones']:
                    print(f"   📞 {phone}")
            else:
                print(f"   ❌ No phone numbers found")
            print(f"   Status: {result['status']}")
        
        # Save to file
        try:
            with open("monday_property_phones.json", "w") as f:
                json.dump(self.results, f, indent=2)
            print(f"\n💾 Results saved to: monday_property_phones.json")
        except Exception as e:
            print(f"\n⚠️  Could not save results file: {e}")
        
        print(f"\n🎉 Processing complete!")

def main():
    """Main function"""
    # API credentials
    MONDAY_API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjMxOTcyMjAwMywiYWFpIjoxMSwidWlkIjo1NDE1NDI4MSwiaWFkIjoiMjAyNC0wMi0wOVQyMzowODo0Ni4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MTI4NDMxMTksInJnbiI6InVzZTEifQ.xshH7gVvlzc89H7bePImbYudk58FLS9vmr6NggMhxeY"
    PROPERTY_RADAR_API_KEY = "a1b7cec841201499fecdfcd9a7124217ed2d51ed"
    BOARD_ID = "9009448650"
    
    # Create integration instance
    integration = MondayPropertyRadarIntegration(MONDAY_API_TOKEN, PROPERTY_RADAR_API_KEY)
    
    # Process the addresses
    integration.process_addresses(BOARD_ID, limit=10)

if __name__ == "__main__":
    main() 