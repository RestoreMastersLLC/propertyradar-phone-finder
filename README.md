# PropertyRadar Phone Finder

A comprehensive integration tool that connects Monday.com with PropertyRadar API to automatically find phone numbers for property addresses.

## Features

- **Monday.com Integration**: Automatically fetch addresses from Monday.com boards
- **PropertyRadar API Integration**: Find property owners and their contact information
- **Smart Cached Data Retrieval**: Intelligent fallback system for already-purchased data
- **Modern Next.js UI**: Clean, responsive interface with dark theme
- **Batch Processing**: Handle multiple addresses simultaneously
- **Export to CSV**: Download results for further analysis
- **Real-time Cost Tracking**: Monitor API usage costs

## Components

### 1. Python Scripts
- `final_working_script.py` - Main script for Monday.com to PropertyRadar integration
- `test_single_address.py` - Test individual addresses
- `monday_property_radar_integration.py` - Core integration logic

### 2. Next.js Web Application
- Modern React-based UI (`propertyradar-ui/`)
- API routes for property lookup
- File upload and direct address entry
- Real-time results display

## Setup & Installation

### Prerequisites
- Python 3.8+
- Node.js 18+
- Monday.com API Token
- PropertyRadar API Key

### Python Environment
```bash
pip install requests python-dotenv
```

### Next.js Application
```bash
cd propertyradar-ui
npm install
npm run dev
```

## Configuration

### API Credentials
Create a `.env` file with:
```
MONDAY_API_TOKEN=your_monday_token_here
PROPERTYRADAR_API_KEY=your_propertyradar_key_here
MONDAY_BOARD_ID=your_board_id_here
```

### Environment Variables for Next.js
Create `propertyradar-ui/.env.local`:
```
PROPERTYRADAR_API_KEY=your_propertyradar_key_here
```

## Usage

### Python Scripts
```bash
# Run full Monday.com integration
python final_working_script.py

# Test single address
python test_single_address.py
```

### Web Application
1. Start the development server: `npm run dev`
2. Navigate to `http://localhost:3001`
3. Enter addresses manually or upload a CSV file
4. Click "Find Phone Numbers" to process
5. Export results to CSV

## API Integration Details

### PropertyRadar API
- **Endpoint**: `https://api.propertyradar.com/v1/properties`
- **Method**: POST with Purchase parameter
- **Authentication**: Bearer token
- **Smart Caching**: Handles "already purchased" data efficiently

### Monday.com API
- **Endpoint**: `https://api.monday.com/v2`
- **Method**: POST with GraphQL queries
- **Authentication**: API token in headers

## Smart Features

### Cached Data Retrieval
The system implements intelligent fallback logic:
1. Try Purchase=0 (check cached data)
2. Try Purchase=1 (purchase new data)
3. If "already purchased" error, try alternative endpoints

### Address Parsing
Robust address parsing supporting various formats:
- Standard format: "123 Main St, City, State 12345"
- Flexible state abbreviations (Ms, TX, Al, etc.)
- Handles directional prefixes (Se, N, etc.)

## Test Results

Successfully tested with addresses including:
- `420 Se Broad St, Fairburn, Ga 30213` - Found 2 phone numbers
- `4210 Earnings Way, New Albany, In 47150` - Found 3 phone numbers
- `410 Williams, Maysville, Ok 73057` - Found 3 phone numbers

## Technology Stack

- **Backend**: Python with requests library
- **Frontend**: Next.js 14, React, TypeScript
- **Styling**: Tailwind CSS
- **APIs**: Monday.com GraphQL, PropertyRadar REST API
- **Data Format**: JSON processing and CSV export

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is proprietary to RestoreMastersLLC.

## Support

For issues or questions, please create an issue in the GitHub repository. 