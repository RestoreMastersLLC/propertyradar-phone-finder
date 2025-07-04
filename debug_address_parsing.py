#!/usr/bin/env python3
"""
Debug address parsing for PropertyRadar
"""
import re

def parse_address(full_address):
    """Parse full address into components for PropertyRadar API"""
    print(f"🔍 Parsing address: {full_address}")
    
    parts = full_address.split(',')
    print(f"📋 Split parts: {parts}")
    
    if len(parts) >= 3:
        street = parts[0].strip()
        city = parts[1].strip()
        
        # Extract state and ZIP from last part
        state_zip = parts[2].strip()
        print(f"🏠 State_zip part: '{state_zip}'")
        
        state_zip_match = re.match(r'([A-Za-z]{2})\s+(\d{5})', state_zip)
        print(f"📍 Regex match: {state_zip_match}")
        
        if state_zip_match:
            state = state_zip_match.group(1).upper()
            zip_code = state_zip_match.group(2)
            
            print(f"✅ Successfully parsed:")
            print(f"   State: '{state}'")
            print(f"   ZIP: '{zip_code}'")
            
            result = {
                "street": street,
                "city": city,
                "state": state,
                "zip": zip_code
            }
            
            print(f"🎯 Final result: {result}")
            return result
        else:
            print(f"❌ Regex match failed for state_zip: '{state_zip}'")
    else:
        print(f"❌ Not enough parts: {len(parts)} (need 3+)")
    
    print(f"❌ Parsing failed - returning None")
    return None

# Test the problematic address
test_address = "4097 Al Highway 69, Guntersville, Al 35976"
result = parse_address(test_address)

print(f"\n🏁 FINAL RESULT:")
print(f"Result: {result}")

if result:
    print(f"✅ SUCCESS! Components:")
    for key, value in result.items():
        print(f"   {key}: {value}")
else:
    print(f"❌ FAILED!") 