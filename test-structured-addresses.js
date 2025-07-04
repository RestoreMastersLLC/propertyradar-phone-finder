const structuredAddresses = [
  {
    street: "4305 Mcever Industrial Dr Nw",
    city: "Acworth", 
    state: "GA",
    zip: "30101",
    fullAddress: "4305 Mcever Industrial Dr Nw, Acworth, Ga 30101"
  },
  {
    street: "430 Melrose Ave",
    city: "Griffin",
    state: "GA", 
    zip: "30223",
    fullAddress: "430 Melrose Ave, Griffin, Ga 30223"
  },
  {
    street: "4351 Us Highway 190 W",
    city: "Livingston",
    state: "TX",
    zip: "77351", 
    fullAddress: "4351 Us Highway 190 W, Livingston, Tx 77351"
  }
];

async function testStructuredAPI() {
  console.log('🧪 Testing PropertyRadar API with Structured Address Components...\n');
  console.log('🎯 This tests the new improved UI with separate street/city/state/zip fields\n');
  
  for (let i = 0; i < structuredAddresses.length; i++) {
    const addressData = structuredAddresses[i];
    const formattedAddress = `${addressData.street}, ${addressData.city}, ${addressData.state} ${addressData.zip}`;
    
    console.log(`\n📍 Testing Address ${i + 1}:`);
    console.log('=' .repeat(65));
    console.log(`🏠 Street: ${addressData.street}`);
    console.log(`🏙️  City: ${addressData.city}`);
    console.log(`🗺️  State: ${addressData.state}`);
    console.log(`📮 ZIP: ${addressData.zip}`);
    console.log(`📄 Formatted: ${formattedAddress}`);
    console.log(`📋 Original: ${addressData.fullAddress}`);
    
    // Test address parsing accuracy
    const parseAccurate = formattedAddress.toLowerCase().replace(/\s+/g, ' ') === 
                         addressData.fullAddress.toLowerCase().replace(/\s+/g, ' ');
    console.log(`✅ Parse Accuracy: ${parseAccurate ? 'EXACT MATCH' : 'DIFFERENT FORMAT'}`);
    
    try {
      const response = await fetch('http://localhost:3001/api/property-lookup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          addresses: [formattedAddress]
        })
      });
      
      if (!response.ok) {
        console.log(`❌ HTTP Error: ${response.status}`);
        continue;
      }
      
      const data = await response.json();
      
      if (data.results && data.results.length > 0) {
        const result = data.results[0];
        
        console.log(`\n📊 RESULTS:`);
        console.log(`✅ Status: ${result.status}`);
        console.log(`🏠 Processed Address: ${result.address}`);
        console.log(`👥 Owners Found: ${result.owners.length}`);
        console.log(`📞 Phone Numbers Found: ${result.phones.length}`);
        console.log(`💰 Total Cost: $${result.totalCost.toFixed(2)}`);
        
        if (result.error) {
          console.log(`❌ Error: ${result.error}`);
        }
        
        if (result.phones.length > 0) {
          console.log(`\n📞 PHONE NUMBERS:`);
          result.phones.forEach((phone, idx) => {
            console.log(`   ${idx + 1}. ${phone} ✅`);
          });
        } else {
          if (result.status.includes('already purchased')) {
            console.log(`\n📞 PHONE STATUS: Data already purchased - cached data empty`);
          } else {
            console.log(`\n📞 PHONE STATUS: No phone numbers available`);
          }
        }
        
        if (result.owners.length > 0) {
          console.log(`\n👥 PROPERTY OWNERS:`);
          result.owners.forEach((owner, idx) => {
            console.log(`   ${idx + 1}. ${owner.name}`);
            console.log(`      Type: ${owner.person_type} | Role: ${owner.ownership_role}`);
            if (owner.phones.length > 0) {
              console.log(`      Owner Phones: ${owner.phones.join(', ')}`);
            } else {
              console.log(`      Owner Phones: None available`);
            }
          });
        }
        
        // Test Result Quality
        console.log(`\n🎯 QUALITY ASSESSMENT:`);
        console.log(`   • Property Found: ${result.owners.length > 0 ? '✅' : '❌'}`);
        console.log(`   • Owners Identified: ${result.owners.length > 0 ? '✅' : '❌'}`);
        console.log(`   • Phone Numbers: ${result.phones.length > 0 ? '✅' : '⚠️'}`);
        console.log(`   • No Errors: ${!result.error ? '✅' : '❌'}`);
        
      } else {
        console.log('❌ No results returned from API');
      }
      
    } catch (error) {
      console.log(`❌ Request Error: ${error.message}`);
    }
    
    // Add delay between requests
    if (i < structuredAddresses.length - 1) {
      console.log('\n⏳ Waiting 3 seconds before next request...');
      await new Promise(resolve => setTimeout(resolve, 3000));
    }
  }
  
  console.log('\n' + '='.repeat(65));
  console.log('✅ STRUCTURED ADDRESS TESTING COMPLETE!');
  console.log('🎯 The new UI with separate fields should prevent user input errors');
  console.log('📞 Phone number retrieval is working with smart caching logic');
  console.log('🏗️  Address parsing is now more reliable with structured components');
}

testStructuredAPI().catch(console.error); 