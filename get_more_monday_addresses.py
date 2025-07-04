#!/usr/bin/env python3
"""
Get more addresses from Monday.com to find residential properties
that might have individual owners with available contact data
"""

import requests
import json

def get_all_monday_addresses(monday_token, board_id, limit=50):
    """Get more addresses from Monday.com board"""
    print(f"📋 Getting up to {limit} addresses from Monday.com board {board_id}...")
    
    url = "https://api.monday.com/v2"
    headers = {
        "Authorization": f"Bearer {monday_token}",
        "Content-Type": "application/json"
    }
    
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
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
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

def extract_address(item):
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

def categorize_address(address):
    """Try to categorize if address is likely residential or commercial"""
    if not address:
        return "unknown"
    
    address_lower = address.lower()
    
    # Commercial indicators
    commercial_indicators = [
        'highway', 'hwy', 'interstate', 'business', 'industrial', 'commerce',
        'corporate', 'office', 'plaza', 'center', 'mall', 'store', 'shop',
        'warehouse', 'facility', 'building', 'complex', 'park', 'blvd',
        'frontage', 'service', 'commercial'
    ]
    
    # Residential indicators  
    residential_indicators = [
        'st', 'street', 'ave', 'avenue', 'rd', 'road', 'ln', 'lane',
        'dr', 'drive', 'way', 'ct', 'court', 'pl', 'place', 'cir', 'circle',
        'apt', 'apartment', 'unit', '#'
    ]
    
    # Check for commercial indicators
    if any(indicator in address_lower for indicator in commercial_indicators):
        return "likely_commercial"
    
    # Check for residential indicators
    if any(indicator in address_lower for indicator in residential_indicators):
        return "likely_residential"
    
    return "unknown"

def main():
    """Get and categorize Monday.com addresses"""
    
    # Configuration
    MONDAY_API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjMxOTcyMjAwMywiYWFpIjoxMSwidWlkIjo1NDE1NDI4MSwiaWFkIjoiMjAyNC0wMi0wOVQyMzowODo0Ni4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MTI4NDMxMTksInJnbiI6InVzZTEifQ.xshH7gVvlzc89H7bePImbYudk58FLS9vmr6NggMhxeY"
    BOARD_ID = "9009448650"
    
    print("🚀 Getting More Addresses from Monday.com")
    print("=" * 60)
    
    # Get more addresses from Monday.com
    items = get_all_monday_addresses(MONDAY_API_TOKEN, BOARD_ID, limit=50)
    
    if not items:
        print("❌ No items found in Monday.com board")
        return
    
    addresses = []
    residential_addresses = []
    commercial_addresses = []
    unknown_addresses = []
    
    print(f"\n📋 Processing {len(items)} addresses...")
    print("=" * 60)
    
    for i, item in enumerate(items, 1):
        address = extract_address(item)
        
        if not address:
            continue
        
        category = categorize_address(address)
        addresses.append((address, category))
        
        print(f"{i:2d}. {address}")
        print(f"    Category: {category}")
        
        if category == "likely_residential":
            residential_addresses.append(address)
        elif category == "likely_commercial":
            commercial_addresses.append(address)
        else:
            unknown_addresses.append(address)
        
        print()
    
    print("=" * 60)
    print("📊 SUMMARY:")
    print(f"   Total Valid Addresses: {len(addresses)}")
    print(f"   Likely Residential: {len(residential_addresses)}")
    print(f"   Likely Commercial: {len(commercial_addresses)}")
    print(f"   Unknown Category: {len(unknown_addresses)}")
    
    if residential_addresses:
        print(f"\n🏠 RESIDENTIAL ADDRESSES TO TEST:")
        for i, addr in enumerate(residential_addresses[:10], 1):
            print(f"   {i}. {addr}")
    
    if commercial_addresses:
        print(f"\n🏢 COMMERCIAL ADDRESSES (likely no personal contact):")
        for i, addr in enumerate(commercial_addresses[:5], 1):
            print(f"   {i}. {addr}")
    
    # Save results
    results = {
        "all_addresses": addresses,
        "residential": residential_addresses,
        "commercial": commercial_addresses,
        "unknown": unknown_addresses
    }
    
    try:
        with open("monday_addresses_categorized.json", "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to: monday_addresses_categorized.json")
    except Exception as e:
        print(f"\n⚠️  Could not save results: {e}")
    
    print(f"\n💡 RECOMMENDATION:")
    if residential_addresses:
        print(f"   Test with residential addresses first - more likely to have individual owners")
        print(f"   Try these addresses in PropertyRadar API to find people like 'CHARLYNE SMITH'")
    else:
        print(f"   Consider getting more addresses from Monday.com or different data sources")

if __name__ == "__main__":
    main() 