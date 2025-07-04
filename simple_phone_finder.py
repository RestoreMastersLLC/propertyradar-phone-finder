#!/usr/bin/env python3
"""
Simple Phone Number Finder for Monday.com Addresses

This script fetches addresses from Monday.com and finds phone numbers using multiple approaches.
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

class SimplePhoneFinder:
    def __init__(self, monday_token: str, property_radar_token: str):
        self.monday_token = monday_token
        self.property_radar_token = property_radar_token
        
        # Monday.com API setup
        self.monday_url = "https://api.monday.com/v2"
        self.monday_headers = {
            "Authorization": f"Bearer {monday_token}",
            "Content-Type": "application/json"
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

    def try_property_radar_simple(self, address: str) -> List[str]:
        """Try simple Property Radar lookup"""
        print(f"🔍 Trying Property Radar for: {address}")
        
        # Try different Property Radar endpoint formats
        endpoints_to_try = [
            f"https://api.propertyradar.com/v1/properties?address={address}",
            f"https://api.propertyradar.com/v1/search?q={address}",
            f"https://api.propertyradar.com/v1/lookup?address={address}"
        ]
        
        headers = {
            "Authorization": f"Bearer {self.property_radar_token}",
            "User-Agent": "Phone-Finder/1.0"
        }
        
        for endpoint in endpoints_to_try:
            try:
                response = requests.get(endpoint, headers=headers, timeout=30)
                print(f"   📡 Trying {endpoint.split('/')[-1]}: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    phones = self.extract_phones_from_data(data)
                    if phones:
                        print(f"   ✅ Found phones via GET: {phones}")
                        return phones
                        
            except Exception as e:
                print(f"   ⚠️  Error with {endpoint}: {e}")
                continue
        
        # Try POST with minimal data
        try:
            post_data = {"address": address}
            response = requests.post("https://api.propertyradar.com/v1/properties", 
                                   headers=headers, json=post_data, timeout=30)
            print(f"   📡 Trying POST: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                phones = self.extract_phones_from_data(data)
                if phones:
                    print(f"   ✅ Found phones via POST: {phones}")
                    return phones
                    
        except Exception as e:
            print(f"   ⚠️  POST error: {e}")
        
        return []

    def try_alternative_sources(self, address: str) -> List[str]:
        """Try alternative property data sources"""
        print(f"🔍 Trying alternative sources for: {address}")
        
        phones = []
        
        # Parse address components for better searching
        parts = address.split(',')
        street_address = parts[0].strip() if parts else address
        
        print(f"   📍 Street address: {street_address}")
        
        # For demo purposes, we'll show what could be tried
        # (These would need proper API keys and endpoints)
        alternative_sources = [
            "Whitepages API",
            "FastPeopleSearch",
            "Spokeo API", 
            "TruePeopleSearch",
            "Public Records APIs"
        ]
        
        for source in alternative_sources:
            print(f"   📞 Could try: {source}")
            # time.sleep(0.1)  # Small delay for demo
        
        return phones

    def extract_phones_from_data(self, data: any) -> List[str]:
        """Extract phone numbers from any data structure"""
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
            # Extract digits only
            digits = ''.join(c for c in str(phone) if c.isdigit())
            if len(digits) == 10:
                formatted = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
                cleaned_phones.append(formatted)
            elif len(digits) == 11 and digits.startswith('1'):
                formatted = f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
                cleaned_phones.append(formatted)
        
        return list(set(cleaned_phones))  # Remove duplicates

    def process_addresses(self, board_id: str, limit: int = 10):
        """Main processing function"""
        print("🚀 Simple Phone Number Finder")
        print("=" * 50)
        
        # Get addresses from Monday.com
        items = self.get_monday_addresses(board_id, limit)
        
        if not items:
            print("❌ No items found")
            return
        
        print(f"\n📋 Processing {len(items)} items...")
        print("=" * 50)
        
        for i, item in enumerate(items, 1):
            print(f"\n📍 Item {i}/{len(items)}")
            print("-" * 30)
            
            address = self.extract_address(item)
            
            if not address:
                print("⚠️  No valid address found")
                self.results.append({
                    "item_id": item.get('id'),
                    "address": "No address",
                    "phones": [],
                    "status": "No address"
                })
                continue
            
            print(f"🏠 Address: {address}")
            
            # Try to find phone numbers
            phones = []
            
            # Try Property Radar first
            phones.extend(self.try_property_radar_simple(address))
            
            # If no phones found, try alternatives
            if not phones:
                phones.extend(self.try_alternative_sources(address))
            
            # Store results
            result = {
                "item_id": item.get('id'),
                "address": address,
                "phones": phones,
                "status": "Found phones" if phones else "No phones found"
            }
            self.results.append(result)
            
            if phones:
                print(f"📞 Found {len(phones)} phone number(s):")
                for phone in phones:
                    print(f"   📞 {phone}")
            else:
                print("📞 No phone numbers found")
            
            time.sleep(1)  # Rate limiting
        
        self.generate_report()

    def generate_report(self):
        """Generate final report"""
        print("\n" + "=" * 50)
        print("📊 PHONE NUMBER SEARCH RESULTS")
        print("=" * 50)
        
        total_addresses = len(self.results)
        addresses_with_phones = sum(1 for r in self.results if r['phones'])
        total_phones = sum(len(r['phones']) for r in self.results)
        
        print(f"\n📈 SUMMARY:")
        print(f"   Total Addresses: {total_addresses}")
        print(f"   Addresses with Phones: {addresses_with_phones}")
        print(f"   Total Phone Numbers: {total_phones}")
        
        print(f"\n📋 DETAILS:")
        for i, result in enumerate(self.results, 1):
            print(f"\n{i}. {result['address']}")
            if result['phones']:
                for phone in result['phones']:
                    print(f"   📞 {phone}")
            else:
                print(f"   ❌ No phones found")
        
        # Save results
        try:
            with open("phone_search_results.json", "w") as f:
                json.dump(self.results, f, indent=2)
            print(f"\n💾 Results saved to: phone_search_results.json")
        except Exception as e:
            print(f"\n⚠️  Could not save results: {e}")

def main():
    # API credentials
    MONDAY_API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjMxOTcyMjAwMywiYWFpIjoxMSwidWlkIjo1NDE1NDI4MSwiaWFkIjoiMjAyNC0wMi0wOVQyMzowODo0Ni4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MTI4NDMxMTksInJnbiI6InVzZTEifQ.xshH7gVvlzc89H7bePImbYudk58FLS9vmr6NggMhxeY"
    PROPERTY_RADAR_API_KEY = "a1b7cec841201499fecdfcd9a7124217ed2d51ed"
    BOARD_ID = "9009448650"
    
    # Create finder instance
    finder = SimplePhoneFinder(MONDAY_API_TOKEN, PROPERTY_RADAR_API_KEY)
    
    # Find phone numbers
    finder.process_addresses(BOARD_ID, limit=10)

if __name__ == "__main__":
    main() 