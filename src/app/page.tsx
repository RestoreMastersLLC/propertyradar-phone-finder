'use client';

import { useState } from 'react';
import axios from 'axios';
import Image from 'next/image';
import { Search, Phone, User, Loader2, Copy, CheckCircle, AlertCircle, XCircle, MapPin } from 'lucide-react';

interface Owner {
  person_key: string;
  name: string;
  ownership_role: string;
  person_type: string;
  phones: string[];
  phoneCost: number;
}

interface LookupResult {
  address: string;
  status: string;
  owners: Owner[];
  phones: string[];
  totalCost: number;
  error?: string;
}

interface ApiResponse {
  results: LookupResult[];
}

interface AddressComponents {
  street: string;
  city: string;
  state: string;
  zip: string;
}

export default function PropertyRadarUI() {
  const [addressComponents, setAddressComponents] = useState<AddressComponents>({
    street: '',
    city: '',
    state: '',
    zip: ''
  });
  const [result, setResult] = useState<LookupResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [copiedPhone, setCopiedPhone] = useState<string | null>(null);

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedPhone(text);
      setTimeout(() => setCopiedPhone(null), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const updateAddressComponent = (field: keyof AddressComponents, value: string) => {
    setAddressComponents(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const isFormValid = () => {
    return addressComponents.street.trim() && 
           addressComponents.city.trim() && 
           addressComponents.state.trim() && 
           addressComponents.zip.trim();
  };

  const formatFullAddress = () => {
    return `${addressComponents.street}, ${addressComponents.city}, ${addressComponents.state} ${addressComponents.zip}`;
  };

  const handleSubmit = async () => {
    if (!isFormValid()) {
      alert('Please fill in all address fields');
      return;
    }

    setLoading(true);
    setResult(null);

    const fullAddress = formatFullAddress();

    try {
      const response = await axios.post<ApiResponse>('/api/property-lookup', {
        addresses: [fullAddress]
      });
      
      if (response.data.results && response.data.results.length > 0) {
        setResult(response.data.results[0]);
      }
    } catch (error) {
      console.error('Error:', error);
      setResult({
        address: fullAddress,
        status: 'Error',
        owners: [],
        phones: [],
        totalCost: 0,
        error: 'An error occurred while processing the address'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent, field: keyof AddressComponents) => {
    if (e.key === 'Enter') {
      // Move to next field or submit if last field
      const fields: (keyof AddressComponents)[] = ['street', 'city', 'state', 'zip'];
      const currentIndex = fields.indexOf(field);
      
      if (currentIndex < fields.length - 1) {
        // Focus next field
        const nextField = fields[currentIndex + 1];
        const nextElement = document.getElementById(nextField);
        nextElement?.focus();
      } else if (isFormValid()) {
        // Submit if last field and form is valid
        handleSubmit();
      }
    }
  };

  const getStatusIcon = (status: string, phonesCount: number) => {
    if (phonesCount > 0) {
      return <CheckCircle className="h-6 w-6 text-green-400" />;
    } else if (status === 'Error') {
      return <XCircle className="h-6 w-6 text-red-400" />;
    } else {
      return <AlertCircle className="h-6 w-6 text-yellow-400" />;
    }
  };

  const getStatusMessage = (result: LookupResult) => {
    if (result.error) {
      return result.error;
    }
    
    if (result.phones.length > 0) {
      return `✅ Success! Found ${result.phones.length} phone number${result.phones.length > 1 ? 's' : ''} for this property`;
    }
    
    if (result.status.includes('already purchased')) {
      return '⚠️ No phone numbers available - Data was previously purchased but not accessible in cache';
    }
    
    if (result.status === 'Success' && result.phones.length === 0) {
      return '⚠️ Property found but no phone numbers are available for this address';
    }
    
    if (result.status === 'No property found') {
      return '❌ No property found at this address - Please verify the address is correct';
    }
    
    if (result.status === 'No owners found') {
      return '⚠️ Property found but no owner information available';
    }
    
    return result.status;
  };

  const clearForm = () => {
    setAddressComponents({
      street: '',
      city: '',
      state: '',
      zip: ''
    });
    setResult(null);
  };

  // US States for dropdown
  const usStates = [
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <Image 
                src="/logo.png" 
                alt="PropertyRadar Logo" 
                width={80} 
                height={80} 
                className="mr-3"
              />
            </div>
            <div className="text-sm text-gray-400">
              Smart cached data retrieval system
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Input Section */}
        <div className="bg-gray-800 rounded-lg shadow-lg p-6 mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold flex items-center">
              <Search className="h-6 w-6 mr-2 text-blue-400" />
              Find Phone Numbers
            </h2>
            {(addressComponents.street || addressComponents.city || addressComponents.state || addressComponents.zip) && (
              <button
                onClick={clearForm}
                className="text-gray-400 hover:text-white text-sm px-3 py-1 rounded-md border border-gray-600 hover:border-gray-500 transition-colors"
              >
                Clear Form
              </button>
            )}
          </div>

          <div className="space-y-4">
            {/* Street Address */}
            <div>
              <label htmlFor="street" className="block text-sm font-medium text-gray-300 mb-2">
                <MapPin className="h-4 w-4 inline mr-1" />
                Street Address
              </label>
              <input
                id="street"
                type="text"
                value={addressComponents.street}
                onChange={(e) => updateAddressComponent('street', e.target.value)}
                onKeyPress={(e) => handleKeyPress(e, 'street')}
                placeholder="e.g., 123 Main St, 4305 Mcever Industrial Dr Nw"
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
              />
            </div>

            {/* City and State Row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* City */}
              <div className="md:col-span-2">
                <label htmlFor="city" className="block text-sm font-medium text-gray-300 mb-2">
                  City
                </label>
                <input
                  id="city"
                  type="text"
                  value={addressComponents.city}
                  onChange={(e) => updateAddressComponent('city', e.target.value)}
                  onKeyPress={(e) => handleKeyPress(e, 'city')}
                  placeholder="e.g., Acworth, Griffin, Livingston"
                  className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                />
              </div>

              {/* State */}
              <div>
                <label htmlFor="state" className="block text-sm font-medium text-gray-300 mb-2">
                  State
                </label>
                <select
                  id="state"
                  value={addressComponents.state}
                  onChange={(e) => updateAddressComponent('state', e.target.value)}
                  onKeyPress={(e) => handleKeyPress(e, 'state')}
                  className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                >
                  <option value="">Select State</option>
                  {usStates.map(state => (
                    <option key={state} value={state}>{state}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* ZIP Code */}
            <div className="max-w-xs">
              <label htmlFor="zip" className="block text-sm font-medium text-gray-300 mb-2">
                ZIP Code
              </label>
              <input
                id="zip"
                type="text"
                value={addressComponents.zip}
                onChange={(e) => updateAddressComponent('zip', e.target.value.replace(/\D/g, '').slice(0, 5))}
                onKeyPress={(e) => handleKeyPress(e, 'zip')}
                placeholder="e.g., 30101"
                maxLength={5}
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
              />
            </div>

            {/* Preview Address */}
            {isFormValid() && (
              <div className="bg-gray-700/30 border border-gray-600 rounded-md p-3">
                <div className="text-sm text-gray-400 mb-1">Preview Address:</div>
                <div className="text-white font-medium">{formatFullAddress()}</div>
              </div>
            )}

            <div className="flex justify-center pt-2">
              <button
                onClick={handleSubmit}
                disabled={loading || !isFormValid()}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-8 py-3 rounded-md font-medium transition-colors flex items-center text-lg"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                    Searching...
                  </>
                ) : (
                  <>
                    <Search className="h-5 w-5 mr-2" />
                    Find Phone Numbers
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Results Section */}
        {result && (
          <div className="bg-gray-800 rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold flex items-center">
                <Phone className="h-6 w-6 mr-2 text-green-400" />
                Results
              </h2>
              {result.totalCost > 0 && (
                <div className="text-right">
                  <div className="text-sm text-gray-400">API Cost</div>
                  <div className="font-semibold text-purple-400 text-lg">
                    ${result.totalCost.toFixed(2)}
                  </div>
                </div>
              )}
            </div>

            {/* Status Section */}
            <div className="mb-6">
              <div className="flex items-center mb-2">
                {getStatusIcon(result.status, result.phones.length)}
                <h3 className="font-semibold text-lg text-white ml-2">
                  {result.address}
                </h3>
              </div>
              <div className={`text-sm font-medium p-3 rounded-md ${
                result.phones.length > 0
                  ? 'bg-green-900/30 text-green-400 border border-green-500/30'
                  : result.error
                  ? 'bg-red-900/30 text-red-400 border border-red-500/30'
                  : 'bg-yellow-900/30 text-yellow-400 border border-yellow-500/30'
              }`}>
                {getStatusMessage(result)}
              </div>
            </div>

            {/* No Phone Numbers - Try Different Address */}
            {result.phones.length === 0 && !result.error && (
              <div className="mb-6 bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <Search className="h-5 w-5 text-blue-400 mr-2" />
                  <h4 className="font-semibold text-lg text-blue-400">Try a Different Address</h4>
                </div>
                <div className="text-gray-300 text-sm space-y-2">
                  <p>No phone numbers are available for this property. Here are some suggestions:</p>
                  <ul className="list-disc list-inside space-y-1 ml-4">
                    <li>Double-check the address spelling and format</li>
                    <li>Try a nearby address or different property</li>
                    <li>Some properties may not have accessible contact information</li>
                    <li>Consider trying commercial properties which often have more contact data</li>
                  </ul>
                </div>
                <div className="mt-3">
                  <button
                    onClick={clearForm}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center"
                  >
                    <Search className="h-4 w-4 mr-1" />
                    Search New Address
                  </button>
                </div>
              </div>
            )}

            {/* Phone Numbers Section */}
            {result.phones.length > 0 && (
              <div className="mb-6">
                <h4 className="text-lg font-semibold mb-3 flex items-center">
                  <Phone className="h-5 w-5 mr-2 text-green-400" />
                  Phone Numbers ({result.phones.length})
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {result.phones.map((phone, index) => (
                    <div
                      key={index}
                      className="bg-green-600 hover:bg-green-700 text-white px-4 py-3 rounded-lg flex items-center justify-between cursor-pointer transition-colors"
                      onClick={() => copyToClipboard(phone)}
                    >
                      <div className="flex items-center">
                        <Phone className="h-4 w-4 mr-2" />
                        <span className="font-medium text-lg">{phone}</span>
                      </div>
                      <div className="flex items-center">
                        {copiedPhone === phone ? (
                          <CheckCircle className="h-4 w-4 text-green-200" />
                        ) : (
                          <Copy className="h-4 w-4 text-green-200" />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
                <div className="text-sm text-gray-400 mt-2 text-center">
                  Click on any phone number to copy it to your clipboard
                </div>
              </div>
            )}

            {/* Property Owners Section */}
            {result.owners.length > 0 && (
              <div>
                <h4 className="text-lg font-semibold mb-3 flex items-center">
                  <User className="h-5 w-5 mr-2 text-blue-400" />
                  Property Owners ({result.owners.length})
                </h4>
                <div className="space-y-3">
                  {result.owners.map((owner, index) => (
                    <div key={index} className="bg-gray-700/50 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center">
                          <User className="h-4 w-4 text-blue-400 mr-2" />
                          <span className="font-medium text-lg">{owner.name}</span>
                        </div>
                        <div className="text-sm text-gray-400">
                          {owner.person_type} • {owner.ownership_role}
                        </div>
                      </div>
                      
                      {owner.phones.length > 0 && (
                        <div className="mt-3">
                          <div className="text-sm text-gray-400 mb-2">Owner Phone Numbers:</div>
                          <div className="flex flex-wrap gap-2">
                            {owner.phones.map((phone, phoneIndex) => (
                              <div
                                key={phoneIndex}
                                className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-full text-sm flex items-center cursor-pointer transition-colors"
                                onClick={() => copyToClipboard(phone)}
                              >
                                <Phone className="h-3 w-3 mr-1" />
                                {phone}
                                {copiedPhone === phone ? (
                                  <CheckCircle className="h-3 w-3 ml-1" />
                                ) : (
                                  <Copy className="h-3 w-3 ml-1" />
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
} 