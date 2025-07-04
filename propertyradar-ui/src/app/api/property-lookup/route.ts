import { NextRequest, NextResponse } from 'next/server';

// PropertyRadar API functionality (converted from Python script)
interface AddressComponents {
  street: string;
  city: string;
  state: string;
  zip: string;
}

interface PropertyResult {
  RadarID: string;
  [key: string]: unknown;
}

interface OwnerInfo {
  person_key: string;
  name: string;
  ownership_role: string;
  person_type: string;
}

interface PhoneResult {
  phones: string[];
  cost: number;
}

function parseAddress(fullAddress: string): AddressComponents | null {
  console.log(`🔍 Parsing address: ${fullAddress}`);
  
  const parts = fullAddress.split(',');
  console.log(`📋 Split parts:`, parts);
  
  if (parts.length >= 3) {
    const street = parts[0].trim();
    const city = parts[1].trim();
    
    // Extract state and ZIP from last part
    const stateZip = parts[2].trim();
    console.log(`🏠 State_zip part: '${stateZip}'`);
    
    const stateZipMatch = stateZip.match(/([A-Za-z]{2})\s+(\d{5})/);
    console.log(`📍 Regex match:`, stateZipMatch);
    
    if (stateZipMatch) {
      const state = stateZipMatch[1].toUpperCase();
      const zip = stateZipMatch[2];
      
      console.log(`✅ Successfully parsed:`);
      console.log(`   Street: '${street}'`);
      console.log(`   City: '${city}'`);
      console.log(`   State: '${state}'`);
      console.log(`   ZIP: '${zip}'`);
      
      return {
        street,
        city,
        state,
        zip
      };
    } else {
      console.log(`❌ Regex match failed for state_zip: '${stateZip}'`);
    }
  } else {
    console.log(`❌ Not enough parts: ${parts.length} (need 3+)`);
  }
  
  console.log(`❌ Parsing failed - returning null`);
  return null;
}

async function searchPropertyRadar(address: string, apiKey: string): Promise<PropertyResult[]> {
  console.log(`🔍 Searching PropertyRadar for: ${address}`);
  
  const components = parseAddress(address);
  if (!components) {
    throw new Error(`Could not parse address: ${address}`);
  }
  
  const url = "https://api.propertyradar.com/v1/properties";
  const headers = {
    "Authorization": `Bearer ${apiKey}`,
    "Content-Type": "application/json"
  };
  
  const params = new URLSearchParams({ "Purchase": "1" });
  
  const requestData = {
    "Criteria": [
      {
        "name": "Address",
        "value": [components.street]
      },
      {
        "name": "City",
        "value": [components.city]
      },
      {
        "name": "State", 
        "value": [components.state]
      },
      {
        "name": "ZipFive",
        "value": [components.zip]
      }
    ]
  };
  
  try {
    const response = await fetch(`${url}?${params}`, {
      method: 'POST',
      headers,
      body: JSON.stringify(requestData)
    });
    
    if (!response.ok) {
      throw new Error(`PropertyRadar API error: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (data.results && data.results.length > 0) {
      return data.results;
    } else {
      return [];
    }
  } catch (error) {
    console.error('Error searching PropertyRadar:', error);
    throw error;
  }
}

async function getOwnersByRadarId(radarId: string, apiKey: string): Promise<OwnerInfo[]> {
  console.log(`👤 Getting owners for RadarID: ${radarId}`);
  
  const url = `https://api.propertyradar.com/v1/properties/${radarId}/persons`;
  const headers = {
    "Authorization": `Bearer ${apiKey}`,
    "Content-Type": "application/json"
  };
  
  const params = new URLSearchParams({ "Purchase": "1" });
  
  try {
    const response = await fetch(`${url}?${params}`, {
      method: 'GET',
      headers
    });
    
    if (!response.ok) {
      throw new Error(`Owners API error: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (data.results && data.results.length > 0) {
      return data.results.map((owner: Record<string, unknown>) => ({
        person_key: (owner.PersonKey as string) || '',
        name: (owner.EntityName as string) || (owner.Name as string) || 'Unknown Owner',
        ownership_role: (owner.OwnershipRole as string) || 'Unknown',
        person_type: (owner.PersonType as string) || 'Unknown'
      }));
    } else {
      return [];
    }
  } catch (error) {
    console.error('Error getting owners:', error);
    throw error;
  }
}

function findPhoneNumbersInResponse(data: unknown): string[] {
  const phones: string[] = [];
  
  function searchRecursive(obj: unknown, path: string = ""): void {
    if (typeof obj === 'object' && obj !== null) {
      if (Array.isArray(obj)) {
        obj.forEach((item, i) => {
          const currentPath = path ? `${path}[${i}]` : `[${i}]`;
          searchRecursive(item, currentPath);
        });
      } else {
        Object.keys(obj as Record<string, unknown>).forEach(key => {
          const currentPath = path ? `${path}.${key}` : key;
          const value = (obj as Record<string, unknown>)[key];
          
          // Look for phone-related keys
          const phoneIndicators = ['phone', 'tel', 'mobile', 'landline', 'number', 'linktext'];
          if (phoneIndicators.some(indicator => key.toLowerCase().includes(indicator))) {
            if (typeof value === 'string' && /\d/.test(value)) {
              // Extract phone number from string
              const phoneMatch = value.match(/(\d{3}[-.]?\d{3}[-.]?\d{4})/);
              if (phoneMatch) {
                phones.push(phoneMatch[1]);
                console.log(`   📞 Found phone in ${currentPath}: ${phoneMatch[1]}`);
              }
            } else if (typeof value === 'object') {
              searchRecursive(value, currentPath);
            }
          } else if (typeof value === 'object') {
            searchRecursive(value, currentPath);
          }
        });
      }
    }
  }
  
  searchRecursive(data);
  
  // Clean and format found phone numbers
  const cleanedPhones: string[] = [];
  [...new Set(phones)].forEach(phone => {
    // Extract just digits
    const digits = phone.replace(/\D/g, '');
    if (digits.length === 10) {
      const formatted = `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6)}`;
      cleanedPhones.push(formatted);
    } else if (digits.length === 11 && digits.startsWith('1')) {
      const formatted = `(${digits.slice(1, 4)}) ${digits.slice(4, 7)}-${digits.slice(7)}`;
      cleanedPhones.push(formatted);
    } else if (digits.length >= 10) {
      cleanedPhones.push(phone);
    }
  });
  
  return cleanedPhones;
}

async function getPhoneNumbersSmart(personKey: string, apiKey: string): Promise<PhoneResult> {
  if (!personKey) {
    return { phones: [], cost: 0 };
  }
  
  console.log(`📞 Getting phone numbers for PersonKey: ${personKey}`);
  
  const url = `https://api.propertyradar.com/v1/persons/${personKey}/Phone`;
  const headers = {
    "Authorization": `Bearer ${apiKey}`,
    "Content-Type": "application/json"
  };
  
  // EXACT LOGIC FROM WORKING PYTHON SCRIPT
  // Strategy 1: Try Purchase=1 first (like our working Python script)
  try {
    console.log(`💰 Step 1: Trying to purchase phone data (Purchase=1)...`);
    const purchaseParams = new URLSearchParams({ "Purchase": "1" });
    const purchaseResponse = await fetch(`${url}?${purchaseParams}`, {
      method: 'POST',
      headers
    });
    
    console.log(`📡 Purchase response status: ${purchaseResponse.status}`);
    
    if (purchaseResponse.ok) {
      const purchaseData = await purchaseResponse.json();
      console.log(`📊 Purchase data:`, JSON.stringify(purchaseData, null, 2));
      
      const phones = findPhoneNumbersInResponse(purchaseData);
      console.log(`📞 Phones found in purchase data: ${JSON.stringify(phones)}`);
      
      if (phones.length > 0) {
        console.log(`✅ Found ${phones.length} phone(s) via purchase`);
        return { phones, cost: purchaseData.totalCost || 0 };
      } else {
        console.log(`⚠️  No phone numbers found in purchase response`);
        if (purchaseData.resultCount > 0) {
          console.log(`📄 API returned ${purchaseData.resultCount} records but no extractable phones`);
        }
      }
      
      return { phones, cost: purchaseData.totalCost || 0 };
    } else if (purchaseResponse.status === 400) {
      const errorText = await purchaseResponse.text();
      console.log(`❌ Purchase error: ${errorText}`);
      
      if (errorText.includes('already purchased') || errorText.includes('not available for purchase')) {
        console.log(`💡 Data already purchased - trying to retrieve cached data...`);
        
        // Strategy 2: Try cached data (Purchase=0) only if purchase failed due to "already purchased"
        try {
          console.log(`🔄 Step 2: Checking cached data (Purchase=0)...`);
          const cachedParams = new URLSearchParams({ "Purchase": "0" });
          const cachedResponse = await fetch(`${url}?${cachedParams}`, {
            method: 'POST',
            headers
          });
          
          console.log(`📡 Cached response status: ${cachedResponse.status}`);
          
          if (cachedResponse.ok) {
            const cachedData = await cachedResponse.json();
            console.log(`📊 Cached data:`, JSON.stringify(cachedData, null, 2));
            
            const phones = findPhoneNumbersInResponse(cachedData);
            console.log(`📞 Phones found in cached data: ${JSON.stringify(phones)}`);
            
            if (phones.length > 0) {
              console.log(`✅ Retrieved ${phones.length} cached phone(s)`);
              return { phones, cost: cachedData.totalCost || 0 };
            } else {
              console.log(`⚠️  No phones in cached data`);
              if (cachedData.resultCount > 0) {
                console.log(`📄 Raw response structure:`);
                console.log(`   Keys: ${Object.keys(cachedData)}`);
                if (cachedData.results) {
                  console.log(`   Results: ${cachedData.results.length} items`);
                  if (cachedData.results.length > 0) {
                    console.log(`   First result sample:`, JSON.stringify(cachedData.results[0], null, 2));
                  }
                }
              }
            }
            
            return { phones, cost: cachedData.totalCost || 0 };
          } else {
            const errorText = await cachedResponse.text();
            console.log(`❌ Cached data error: ${cachedResponse.status} - ${errorText}`);
          }
        } catch (error) {
          console.log('❌ Cached data error:', error);
        }
        
        console.log(`⚠️  Data already purchased but couldn't retrieve: ${errorText}`);
        
        // Strategy 3: Try alternative endpoints for purchased data (like our working Python script)
        console.log(`🔄 Step 3: Trying alternative endpoints for purchased phone data...`);
        const altPhones = await getPhoneDataAlternativeEndpoints(personKey, apiKey, headers);
        if (altPhones.length > 0) {
          return { phones: altPhones, cost: 0 };
        }
        
        return { phones: [], cost: 0 };
      } else {
        console.log(`❌ Phone API error: ${purchaseResponse.status}`);
        return { phones: [], cost: 0 };
      }
    } else {
      console.log(`❌ Phone API error: ${purchaseResponse.status}`);
      return { phones: [], cost: 0 };
    }
  } catch (error) {
    console.error('❌ Error getting phone numbers:', error);
    return { phones: [], cost: 0 };
  }
}

async function getPhoneDataAlternativeEndpoints(personKey: string, apiKey: string, headers: Record<string, string>): Promise<string[]> {
  console.log(`🔄 Trying alternative endpoints for purchased phone data...`);
  
  // Alternative endpoints from our working Python script
  const alternativeEndpoints = [
    `https://api.propertyradar.com/v1/persons/${personKey}`,  // Person details endpoint
    `https://api.propertyradar.com/v1/persons/${personKey}/contact`,  // Contact endpoint
    `https://api.propertyradar.com/v1/persons/${personKey}/contacts`,  // Contacts endpoint
  ];
  
  for (const endpoint of alternativeEndpoints) {
    const endpointName = endpoint.split('/').pop() || 'unknown';
    console.log(`   🔍 Trying ${endpointName} endpoint...`);
    
    // Try both Purchase=0 and Purchase=1 for each endpoint
    for (const purchaseMode of [0, 1]) {
      const params = new URLSearchParams({ "Purchase": purchaseMode.toString() });
      
      try {
        const response = await fetch(`${endpoint}?${params}`, {
          method: 'GET',
          headers
        });
        
        if (response.ok) {
          const data = await response.json();
          const phones = findPhoneNumbersInResponse(data);
          
          if (phones.length > 0) {
            console.log(`   ✅ Found phones via ${endpointName} (Purchase=${purchaseMode})`);
            phones.forEach(phone => console.log(`      📞 ${phone}`));
            return phones;
          }
        }
             } catch {
         // Continue trying other endpoints
         continue;
       }
    }
  }
  
  return [];
}

export async function POST(request: NextRequest) {
  try {
    const { addresses } = await request.json();
    
    if (!addresses || !Array.isArray(addresses)) {
      return NextResponse.json({ error: 'Invalid addresses format' }, { status: 400 });
    }
    
    const API_KEY = "a1b7cec841201499fecdfcd9a7124217ed2d51ed";
    const results = [];
    
    for (const address of addresses) {
      console.log(`Processing address: ${address}`);
      
      try {
        // Search for property
        const propertyResults = await searchPropertyRadar(address, API_KEY);
        
        if (propertyResults.length === 0) {
          results.push({
            address,
            status: 'No property found',
            owners: [],
            phones: [],
            totalCost: 0
          });
          continue;
        }
        
        // Get owners for each property
        const allOwners: OwnerInfo[] = [];
        for (const property of propertyResults) {
          if (property.RadarID) {
            const owners = await getOwnersByRadarId(property.RadarID, API_KEY);
            allOwners.push(...owners);
          }
        }
        
        if (allOwners.length === 0) {
          results.push({
            address,
            status: 'No owners found',
            owners: [],
            phones: [],
            totalCost: 0
          });
          continue;
        }
        
        // Get phone numbers for each owner
        const ownerDetails = [];
        let totalCost = 0;
        const allPhones: string[] = [];
        let hasAlreadyPurchasedData = false;
        
        for (const owner of allOwners) {
          const phoneResult = await getPhoneNumbersSmart(owner.person_key, API_KEY);
          
          ownerDetails.push({
            ...owner,
            phones: phoneResult.phones,
            phoneCost: phoneResult.cost
          });
          
          totalCost += phoneResult.cost;
          allPhones.push(...phoneResult.phones);
          
          // Track if we encountered "already purchased" scenario
          if (phoneResult.phones.length === 0 && phoneResult.cost === 0) {
            hasAlreadyPurchasedData = true;
          }
        }
        
        // Determine status message based on results
        let status = 'Success';
        if (allPhones.length === 0) {
          if (hasAlreadyPurchasedData) {
            status = 'Data already purchased - no phone numbers available in cache';
          } else {
            status = 'Property found but no phone numbers available';
          }
        } else {
          status = `Found ${allPhones.length} phone number${allPhones.length > 1 ? 's' : ''}`;
        }
        
        results.push({
          address,
          status,
          owners: ownerDetails,
          phones: [...new Set(allPhones)], // Remove duplicates
          totalCost
        });
        
      } catch (error) {
        console.error(`Error processing ${address}:`, error);
        results.push({
          address,
          status: 'Error',
          error: error instanceof Error ? error.message : 'Unknown error',
          owners: [],
          phones: [],
          totalCost: 0
        });
      }
      
      // Add small delay to avoid rate limiting
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    return NextResponse.json({ results });
    
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
} 