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
python3 csv-to-api.py <xlsx-file> <api-url> <admin-api-key>
```

### Parameters
- `xlsx-file`: Local XLSX file path
- `api-url`: API Gateway URL (from CloudFormation outputs)
- `admin-api-key`: Admin API key (Available in Secrets Manager)

### Example
```bash
cd utility
python3 csv-to-api.py customers.xlsx https://abc123.execute-api.us-east-1.amazonaws.com/dev your-api-key-here
```

## XLSX Format

### Make sure first row has column names . Three columns are mandatory "Customer" , "SONum", "SOLine" ###

Example XLSX with headers:
 | Customer | SONum | SOLine |
|-------------|---------------|-------|
| ABC | 10932 | 1 |
| XYZ | 3235 | 1 |
| XYZ | 3235 | 2 |

## How It Works

1. Authenticates with Admin API Key
2. Reads XLSX file from same directory
3. For each row, creates PUT request to `/admin/upsert` endpoint
4. Stores all XLSX columns in `data` attribute with automatic type conversion
5. Reports processing results

## Error Handling

- Shows total count of successfully processed records