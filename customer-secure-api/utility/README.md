# XLSX to API Utility

Standalone utility to read local XLSX files and insert data via the existing POST data API.

## Setup

Install dependencies:
```bash
cd utility
pip install -r requirements-utility.txt
```
#### Note Sometimes pip and python packages are installed as pip3 and python3 

## Usage

```bash
cd utility
python3 csv-to-api.py <xlsx-file> <api-url> <api-key>
```

### Parameters
- `xlsx-file`: Local XLSX file path
- `api-url`: API Gateway URL (from CloudFormation outputs)
- `api-key`: Customer API key (created via admin endpoint)

### Example
```bash
cd utility
python3 csv-to-api.py customers.xlsx https://abc123.execute-api.us-east-1.amazonaws.com/dev your-api-key-here
```

## XLSX Format

Same format as S3 processor:
- **Column 1**: customer_id
- **Column 2**: customer_name  
- **Additional columns**: Any extra data

Example XLSX with headers:
 | customer_name | email | phone |
|-------------|---------------|-------|-------|
| John Doe | john@example.com | 555-1234 |
| Jane Smith | jane@example.com | 555-5678 |

## How It Works

1. Authenticates with API using provided API key
2. Gets JWT token for subsequent requests
3. Reads XLSX file from same directory
4. For each row, creates POST request to `/data` endpoint
5. Uses customer_name (column 2) as mandatory `name` field
6. Stores all XLSX columns in `data` attribute with automatic type conversion
7. Reports processing results

## Error Handling

- Skips rows with missing customer_id or customer_name
- Reports failed insertions but continues processing
- Shows total count of successfully processed records