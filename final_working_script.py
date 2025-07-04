#!/usr/bin/env python3
"""
✅ FINAL WORKING PropertyRadar Contact Finder

This script successfully integrates Monday.com and PropertyRadar APIs:
✅ Correct PropertyRadar API format discovered
✅ Purchase parameter in query string
✅ Address components format (Address, City, State, ZipFive)
✅ Bearer token authentication working
✅ Phone numbers via /v1/persons/{PersonKey}/Phone
✅ Email addresses via /v1/persons/{PersonKey}/Email

⚠️  NOTE: Set USE_PAID_SEARCH=True for real results (will charge account)
"""

import requests
import json
import time
import re
from datetime import datetime

def get_monday_addresses(monday_token, board_id, limit=10):
    """Get addresses from Monday.com board"""
    print(f"📋 Getting addresses from Monday.com board {board_id}...")
    
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

def parse_address(full_address):
    """Parse full address into components for PropertyRadar API"""
    # Try to extract components from full address
    # Format: "400 LAS COLINAS BLVD E, IRVING, TX 75039"
    # Also handles: "1521 S Frontage Rd, Columbus, Ms 39701"
    
    parts = full_address.split(',')
    
    if len(parts) >= 3:
        street = parts[0].strip()
        city = parts[1].strip()
        
        # Extract state and ZIP from last part
        state_zip = parts[2].strip()
        # Updated regex to handle mixed case states like "Ms", "Tx", "TX"
        state_zip_match = re.match(r'([A-Za-z]{2})\s+(\d{5})', state_zip)
        
        if state_zip_match:
            state = state_zip_match.group(1).upper()  # Convert to uppercase
            zip_code = state_zip_match.group(2)
            
            return {
                "street": street,
                "city": city,
                "state": state,
                "zip": zip_code
            }
    
    # If standard format fails, try other patterns
    # Handle formats like "1521 S Frontage Rd, Columbus, Ms 39701"
    if len(parts) >= 2:
        street = parts[0].strip()
        city_state_zip = parts[1].strip()
        
        # Try to extract city, state, ZIP from combined string
        # Pattern: "Columbus, Ms 39701" or "Columbus Ms 39701"
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

def search_property_with_propertyradar(address, api_key, use_paid_search=False):
    """
    Search for property using the WORKING PropertyRadar API format
    
    ✅ WORKING FORMAT:
    - URL: https://api.propertyradar.com/v1/properties
    - Method: POST
    - Auth: Bearer token in Authorization header
    - Purchase: Query parameter (not in body!)
    - Criteria: Request body with separate address components
    """
    print(f"🔍 Searching PropertyRadar for: {address}")
    
    # Parse address into components
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
        "Content-Type": "application/json",
        "User-Agent": "PropertyRadar-Phone-Finder/1.0"
    }
    
    # ✅ Purchase parameter goes in QUERY STRING (not request body!)
    params = {
        "Purchase": 1 if use_paid_search else 0
    }
    
    # ✅ Use separate address components (NOT SiteAddress!)
    request_data = {
        "Criteria": [
            {
                "name": "Address",      # Street only (no city/state/zip)
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
    
    if use_paid_search:
        print(f"💰 WARNING: Using Purchase=1 - This will charge your account!")
    else:
        print(f"🆓 Using Purchase=0 - Test mode (may not return results)")
    
    try:
        response = requests.post(url, 
                               headers=headers, 
                               json=request_data,
                               params=params,
                               timeout=30)
        
        print(f"📡 PropertyRadar response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Track costs from property search
            total_cost = data.get('totalCost', 0)
            result_count = data.get('resultCount', 0)
            
            print(f"💰 Property Search Cost: ${total_cost}")
            print(f"📊 Properties Found: {result_count}")
            
            if 'results' in data and data['results']:
                print(f"✅ Found {len(data['results'])} property result(s)")
                return data['results']
            else:
                if not use_paid_search:
                    print(f"⚠️  No results in test mode. Set use_paid_search=True for real data.")
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

def extract_owner_info(property_results, api_key):
    """Extract owner information from PropertyRadar results using correct API endpoints"""
    owners = []
    
    for result in property_results:
        print(f"📋 Analyzing property result...")
        
        # Get RadarID for owner lookup
        radar_id = result.get('RadarID')
        if not radar_id:
            print(f"❌ No RadarID found in property result")
            continue
        
        print(f"🔍 Found RadarID: {radar_id}")
        
        # Get owner information using the correct endpoint
        owner_data = get_owners_by_radar_id(radar_id, api_key)
        
        if owner_data:
            owners.extend(owner_data)
    
    print(f"✅ Extracted {len(owners)} owner(s)")
    return owners

def get_owners_by_radar_id(radar_id, api_key):
    """Get owner information using PropertyRadar Persons API"""
    print(f"👤 Getting owners for RadarID: {radar_id}")
    
    url = f"https://api.propertyradar.com/v1/properties/{radar_id}/persons"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    params = {"Purchase": 1}  # Paid lookup for owner data
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        print(f"📡 Owners API response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Track costs from owners search
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
                        "mail_address": owner.get('MailAddress', [])
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

def get_phone_numbers_for_owner(person_key, api_key):
    """Get phone numbers using PropertyRadar Phone API - Check cached data FIRST"""
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
    
    # Strategy 2: Try alternative endpoints for purchased data
    print(f"🔄 Step 2: Trying alternative endpoints for purchased data...")
    alt_phones, alt_cost = get_phone_data_alternative_endpoints(person_key, api_key, headers)
    if alt_phones:
        return alt_phones, alt_cost
    
    # Strategy 3: Only try to purchase new data if no cached data found (Purchase=1)
    print(f"💰 Step 3: No cached data found - trying to purchase new phone data...")
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
            
            phones = extract_phones_from_data(data)
            
            if phones:
                print(f"✅ Found {len(phones)} phone number(s) via purchase")
                for phone in phones:
                    print(f"   📞 {phone}")
                return phones, float(total_cost)
            else:
                print(f"⚠️  No phone numbers found in purchase response")
                if result_count > 0:
                    print(f"📄 API returned {result_count} records but no extractable phones")
            
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
            
            # Use comprehensive phone search
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
                
        else:
            print(f"❌ Cached data error: {response.status_code}")
            if response.status_code == 400:
                print(f"   Error message: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting cached data: {e}")
    
    return [], 0

def get_phone_data_alternative_endpoints(person_key, api_key, headers):
    """Try alternative endpoints that might show already-purchased data"""
    print(f"🔄 Step 3: Trying alternative endpoints for purchased data...")
    
    # Alternative endpoints to try
    alternative_endpoints = [
        f"https://api.propertyradar.com/v1/persons/{person_key}",  # Person details endpoint
        f"https://api.propertyradar.com/v1/persons/{person_key}/contact",  # Contact endpoint
        f"https://api.propertyradar.com/v1/persons/{person_key}/contacts",  # Contacts endpoint
    ]
    
    for endpoint in alternative_endpoints:
        endpoint_name = endpoint.split('/')[-1]
        print(f"   🔍 Trying {endpoint_name} endpoint...")
        
        # Try both Purchase=0 and Purchase=1 for each endpoint
        for purchase_mode in [0, 1]:
            params = {"Purchase": purchase_mode}
            
            try:
                response = requests.get(endpoint, headers=headers, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    phones = find_phone_numbers_in_response_comprehensive(data)
                    
                    if phones:
                        print(f"   ✅ Found phones via {endpoint_name} (Purchase={purchase_mode})")
                        for phone in phones:
                            print(f"      📞 {phone}")
                        return phones, 0  # No cost for already-purchased data
                    
            except Exception as e:
                pass  # Continue trying other endpoints
    
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

def get_emails_for_owner(person_key, api_key):
    """Get email addresses using PropertyRadar Email API - Check cached data FIRST"""
    if not person_key:
        print(f"⚠️  No PersonKey available - cannot get emails")
        return [], 0
    
    print(f"📧 Getting emails for PersonKey: {person_key}")
    
    url = f"https://api.propertyradar.com/v1/persons/{person_key}/Email"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Strategy 1: Try to get already-purchased data FIRST (Purchase=0)
    print(f"🔄 Step 1: Checking for already-purchased email data (Purchase=0)...")
    cached_emails, cached_cost = get_cached_email_data(person_key, api_key, url, headers)
    if cached_emails:
        return cached_emails, cached_cost
    
    # Strategy 2: Try alternative endpoints for purchased data
    print(f"🔄 Step 2: Trying alternative endpoints for purchased email data...")
    alt_emails, alt_cost = get_email_data_alternative_endpoints(person_key, api_key, headers)
    if alt_emails:
        return alt_emails, alt_cost
    
    # Strategy 3: Only try to purchase new data if no cached data found (Purchase=1)
    print(f"💰 Step 3: No cached data found - trying to purchase new email data...")
    params = {"Purchase": 1}
    
    try:
        response = requests.post(url, headers=headers, params=params, timeout=30)
        print(f"📡 Email API response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            total_cost = data.get('totalCost', 0)
            result_count = data.get('resultCount', 0)
            
            print(f"💰 Email API Cost: ${total_cost}")
            print(f"📊 Email Records: {result_count}")
            
            emails = extract_emails_from_data(data)
            
            if emails:
                print(f"✅ Found {len(emails)} email address(es) via purchase")
                for email in emails:
                    print(f"   📧 {email}")
                return emails, float(total_cost)
            else:
                print(f"⚠️  No email addresses found in purchase response")
                if result_count > 0:
                    print(f"📄 API returned {result_count} records but no extractable emails")
            
            return emails, float(total_cost)
            
        elif response.status_code == 400:
            error_msg = response.text
            if "already purchased" in error_msg or "not available for purchase" in error_msg:
                print(f"💡 Data already purchased but couldn't retrieve via cached methods")
                print(f"⚠️  Error: {error_msg}")
                return [], 0
            else:
                print(f"❌ Email API error: {response.status_code}")
                print(f"Error: {response.text}")
                return [], 0
        else:
            print(f"❌ Email API error: {response.status_code}")
            print(f"Error: {response.text}")
            return [], 0
            
    except Exception as e:
        print(f"❌ Error getting email addresses: {e}")
        return [], 0

def get_cached_email_data(person_key, api_key, url, headers):
    """Try to get already-purchased email data using Purchase=0"""
    print(f"🔄 Checking cached email data (Purchase=0)...")
    
    params = {"Purchase": 0}
    
    try:
        response = requests.post(url, headers=headers, params=params, timeout=30)
        print(f"📡 Cached email response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            total_cost = data.get('totalCost', 0)
            result_count = data.get('resultCount', 0)
            
            print(f"💰 Cached email cost: ${total_cost}")
            print(f"📊 Cached email records: {result_count}")
            
            # Use comprehensive email search
            emails = find_emails_in_response_comprehensive(data)
            
            if emails:
                print(f"✅ Retrieved {len(emails)} cached email address(es)")
                for email in emails:
                    print(f"   📧 {email}")
                return emails, float(total_cost)
            else:
                print(f"⚠️  No emails in cached data")
                if result_count > 0:
                    print(f"📄 Raw response structure:")
                    print(f"   Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    if 'results' in data:
                        print(f"   Results: {len(data['results'])} items")
                        if data['results']:
                            print(f"   First result keys: {list(data['results'][0].keys()) if isinstance(data['results'][0], dict) else 'Not a dict'}")
                
        else:
            print(f"❌ Cached email error: {response.status_code}")
            if response.status_code == 400:
                print(f"   Error message: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting cached email data: {e}")
    
    return [], 0

def get_email_data_alternative_endpoints(person_key, api_key, headers):
    """Try alternative endpoints that might show already-purchased email data"""
    print(f"🔄 Step 3: Trying alternative endpoints for purchased email data...")
    
    # Alternative endpoints to try
    alternative_endpoints = [
        f"https://api.propertyradar.com/v1/persons/{person_key}",  # Person details endpoint
        f"https://api.propertyradar.com/v1/persons/{person_key}/contact",  # Contact endpoint
        f"https://api.propertyradar.com/v1/persons/{person_key}/contacts",  # Contacts endpoint
    ]
    
    for endpoint in alternative_endpoints:
        endpoint_name = endpoint.split('/')[-1]
        print(f"   🔍 Trying {endpoint_name} endpoint...")
        
        # Try both Purchase=0 and Purchase=1 for each endpoint
        for purchase_mode in [0, 1]:
            params = {"Purchase": purchase_mode}
            
            try:
                response = requests.get(endpoint, headers=headers, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    emails = find_emails_in_response_comprehensive(data)
                    
                    if emails:
                        print(f"   ✅ Found emails via {endpoint_name} (Purchase={purchase_mode})")
                        for email in emails:
                            print(f"      📧 {email}")
                        return emails, 0  # No cost for already-purchased data
                    
            except Exception as e:
                pass  # Continue trying other endpoints
    
    return [], 0

def find_emails_in_response_comprehensive(data):
    """Comprehensive search for email addresses in any API response"""
    emails = []
    
    def search_recursive(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                
                # Look for email-related keys
                email_indicators = ['email', 'mail', 'linktext']
                if any(indicator in key.lower() for indicator in email_indicators):
                    if isinstance(value, str) and '@' in value and '.' in value:
                        emails.append(value)
                    elif isinstance(value, (list, dict)):
                        search_recursive(value, current_path)
                elif isinstance(value, (dict, list)):
                    search_recursive(value, current_path)
                    
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                current_path = f"{path}[{i}]" if path else f"[{i}]"
                search_recursive(item, current_path)
    
    search_recursive(data)
    
    # Clean and validate found email addresses
    cleaned_emails = []
    for email in set(emails):  # Remove duplicates
        email = email.strip()
        if '@' in email and '.' in email and len(email) > 5:
            cleaned_emails.append(email)
    
    return cleaned_emails

def extract_emails_from_data(data):
    """Extract and format email addresses from API response"""
    emails = []
    
    def find_emails_recursive(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if 'email' in key.lower() and value:
                    emails.append(str(value))
                elif isinstance(value, (dict, list)):
                    find_emails_recursive(value)
        elif isinstance(obj, list):
            for item in obj:
                find_emails_recursive(item)
    
    find_emails_recursive(data)
    
    # Clean and validate email addresses
    cleaned_emails = []
    for email in emails:
        email = str(email).strip()
        if '@' in email and '.' in email:
            cleaned_emails.append(email)
    
    return list(set(cleaned_emails))  # Remove duplicates

def extract_phones_from_data(data):
    """Extract and format phone numbers from API response"""
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
        elif len(digits) >= 10:
            cleaned_phones.append(phone)
    
    return list(set(cleaned_phones))  # Remove duplicates

def main():
    """Main function to find phone numbers and emails for Monday.com addresses"""
    
    # Configuration
    MONDAY_API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjMxOTcyMjAwMywiYWFpIjoxMSwidWlkIjo1NDE1NDI4MSwiaWFkIjoiMjAyNC0wMi0wOVQyMzowODo0Ni4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MTI4NDMxMTksInJnbiI6InVzZTEifQ.xshH7gVvlzc89H7bePImbYudk58FLS9vmr6NggMhxeY"
    PROPERTY_RADAR_API_KEY = "a1b7cec841201499fecdfcd9a7124217ed2d51ed"
    BOARD_ID = "9009448650"
    
    # Search mode - SET TO TRUE FOR REAL RESULTS (WILL CHARGE!)
    USE_PAID_SEARCH = True  # ENABLED: Will charge PropertyRadar account for real results
    
    print("🚀 PropertyRadar Contact Finder - SMART CACHED DATA RETRIEVAL")
    print("=" * 60)
    print("✅ Using verified PropertyRadar API format:")
    print("   - Purchase parameter in query string")
    print("   - Address components format (Address, City, State, ZipFive)")
    print("   - Bearer token authentication")
    print("   - Phone API: /v1/persons/{PersonKey}/Phone")
    print("   - Email API: /v1/persons/{PersonKey}/Email")
    print("=" * 60)
    print("🔄 SMART STRATEGY: Check cached data FIRST, then alternative endpoints")
    print("💰 Will only try to purchase new data if no cached data found")
    print("=" * 60)
    
    if USE_PAID_SEARCH:
        print("💰 WARNING: Using paid search mode - will charge your account!")
    else:
        print("🆓 Using test mode - may not return property data")
    print()
    
    # Get addresses from Monday.com - prioritize residential addresses
    items = get_monday_addresses(MONDAY_API_TOKEN, BOARD_ID, limit=25)  # Get more addresses
    
    if not items:
        print("❌ No items found in Monday.com board")
        return
    
    results = []
    
    print(f"\n📋 Processing {len(items)} addresses...")
    print("=" * 60)
    
    for i, item in enumerate(items, 1):
        print(f"\n🏠 Address {i}/{len(items)}")
        print("-" * 40)
        
        address = extract_address(item)
        
        if not address:
            print("⚠️  No valid address found")
            results.append({
                "address": "No address",
                "owners": [],
                "phones": [],
                "emails": [],
                "status": "No address"
            })
            continue
        
        print(f"📍 Address: {address}")
        
        # Search PropertyRadar
        property_results = search_property_with_propertyradar(
            address, 
            PROPERTY_RADAR_API_KEY, 
            USE_PAID_SEARCH
        )
        
        if not property_results:
            results.append({
                "address": address,
                "owners": [],
                "phones": [],
                "emails": [],
                "status": "No property data"
            })
            continue
        
        # Extract owners
        owners = extract_owner_info(property_results, PROPERTY_RADAR_API_KEY)
        
        if not owners:
            results.append({
                "address": address,
                "owners": [],
                "phones": [],
                "emails": [],
                "status": "No owners found"
            })
            continue
        
        # Get phone numbers and emails for each owner
        all_phones = []
        all_emails = []
        owner_details = []
        
        for owner in owners:
            owner_name = owner.get('name', 'Unknown')
            person_key = owner.get('person_key')
            
            print(f"👤 Processing owner: {owner_name}")
            
            if person_key and USE_PAID_SEARCH:
                # Get phone numbers
                owner_phones, phone_cost = get_phone_numbers_for_owner(person_key, PROPERTY_RADAR_API_KEY)
                
                # Get email addresses
                owner_emails, email_cost = get_emails_for_owner(person_key, PROPERTY_RADAR_API_KEY)
                
                # Track total costs
                total_phone_cost = phone_cost
                total_email_cost = email_cost
                
                print(f"💰 Total costs for {owner_name}: Phone ${phone_cost}, Email ${email_cost}")
            else:
                owner_phones = []
                owner_emails = []
                total_phone_cost = 0
                total_email_cost = 0
                if not person_key:
                    print(f"⚠️  No PersonKey for {owner_name}")
                if not USE_PAID_SEARCH:
                    print(f"⚠️  Phone/Email lookup disabled in test mode")
            
            owner_details.append({
                "name": owner_name,
                "person_key": person_key,
                "phones": owner_phones,
                "emails": owner_emails,
                "phone_cost": total_phone_cost,
                "email_cost": total_email_cost
            })
            
            all_phones.extend(owner_phones)
            all_emails.extend(owner_emails)
        
        # Store results
        result = {
            "address": address,
            "owners": owner_details,
            "phones": list(set(all_phones)),  # Remove duplicates
            "emails": list(set(all_emails)),  # Remove duplicates
            "status": "Success" if (all_phones or all_emails) else "No contact info found"
        }
        results.append(result)
        
        if all_phones or all_emails:
            print(f"🎉 Found contact info for {address}")
            if all_phones:
                print(f"   📞 {len(set(all_phones))} phone number(s):")
                for phone in set(all_phones):
                    print(f"      📞 {phone}")
            if all_emails:
                print(f"   📧 {len(set(all_emails))} email address(es):")
                for email in set(all_emails):
                    print(f"      📧 {email}")
        else:
            print(f"📞 No contact information found for {address}")
        
        # Rate limiting
        time.sleep(2)
    
    # Generate final report
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS")
    print("=" * 60)
    
    total_addresses = len(results)
    addresses_with_phones = sum(1 for r in results if r['phones'])
    addresses_with_emails = sum(1 for r in results if r['emails'])
    addresses_with_contact = sum(1 for r in results if r['phones'] or r['emails'])
    total_phones = sum(len(r['phones']) for r in results)
    total_emails = sum(len(r['emails']) for r in results)
    
    # Calculate total costs
    total_phone_cost = sum(
        sum(owner.get('phone_cost', 0) for owner in r['owners']) 
        for r in results
    )
    total_email_cost = sum(
        sum(owner.get('email_cost', 0) for owner in r['owners']) 
        for r in results
    )
    total_cost = total_phone_cost + total_email_cost
    
    print(f"\n📈 SUMMARY:")
    print(f"   Total Addresses: {total_addresses}")
    print(f"   Addresses with Contact Info: {addresses_with_contact}")
    print(f"   Addresses with Phones: {addresses_with_phones}")
    print(f"   Addresses with Emails: {addresses_with_emails}")
    print(f"   Total Phone Numbers: {total_phones}")
    print(f"   Total Email Addresses: {total_emails}")
    print(f"\n💰 COST BREAKDOWN:")
    print(f"   Total Phone API Costs: ${total_phone_cost:.2f}")
    print(f"   Total Email API Costs: ${total_email_cost:.2f}")
    print(f"   Total API Costs: ${total_cost:.2f}")
    print(f"   (Note: Property and Owner searches are FREE)")
    
    print(f"\n📋 DETAILED RESULTS:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['address']}")
        print(f"   Status: {result['status']}")
        
        for owner in result['owners']:
            print(f"   👤 {owner['name']}")
            for phone in owner['phones']:
                print(f"      📞 {phone}")
            for email in owner['emails']:
                print(f"      📧 {email}")
        
        if result['phones'] or result['emails']:
            if result['phones']:
                print(f"   📞 All phones: {', '.join(result['phones'])}")
            if result['emails']:
                print(f"   📧 All emails: {', '.join(result['emails'])}")
    
    # Save results
    try:
        with open("propertyradar_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to: propertyradar_results.json")
    except Exception as e:
        print(f"\n⚠️  Could not save results: {e}")
    
    print(f"\n🎯 PropertyRadar Contact Finder completed!")
    if not USE_PAID_SEARCH:
        print(f"💡 TIP: Set USE_PAID_SEARCH=True for real property, phone, and email data")

if __name__ == "__main__":
    main() 