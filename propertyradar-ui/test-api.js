const addresses = [
  "4305 Mcever Industrial Dr Nw, Acworth, Ga 30101",
  "430 Melrose Ave, Griffin, Ga 30223", 
  "4351 Us Highway 190 W, Livingston, Tx 77351"
];

async function testAPI() {
  console.log('🧪 Testing PropertyRadar API systematically...\n');
  
  for (let i = 0; i < addresses.length; i++) {
    const address = addresses[i];
    console.log(`\n📍 Testing Address ${i + 1}: ${address}`);
    console.log('=' .repeat(60));
    
    try {
      const response = await fetch('http://localhost:3001/api/property-lookup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          addresses: [address]
        })
      });
      
      if (!response.ok) {
        console.log(`❌ HTTP Error: ${response.status}`);
        continue;
      }
      
      const data = await response.json();
      
      if (data.results && data.results.length > 0) {
        const result = data.results[0];
        
        console.log(`✅ Status: ${result.status}`);
        console.log(`🏠 Address: ${result.address}`);
        console.log(`👥 Owners Found: ${result.owners.length}`);
        console.log(`📞 Phone Numbers Found: ${result.phones.length}`);
        console.log(`💰 Total Cost: $${result.totalCost.toFixed(2)}`);
        
        if (result.error) {
          console.log(`❌ Error: ${result.error}`);
        }
        
        if (result.phones.length > 0) {
          console.log(`📞 Phone Numbers:`);
          result.phones.forEach(phone => console.log(`   • ${phone}`));
        }
        
        if (result.owners.length > 0) {
          console.log(`👥 Owners:`);
          result.owners.forEach(owner => {
            console.log(`   • ${owner.name} (${owner.person_type})`);
            if (owner.phones.length > 0) {
              console.log(`     Phones: ${owner.phones.join(', ')}`);
            }
          });
        }
        
      } else {
        console.log('❌ No results returned');
      }
      
    } catch (error) {
      console.log(`❌ Error: ${error.message}`);
    }
    
    // Add delay between requests
    if (i < addresses.length - 1) {
      console.log('\n⏳ Waiting 2 seconds before next request...');
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  }
  
  console.log('\n✅ API Testing Complete!');
}

testAPI().catch(console.error); 