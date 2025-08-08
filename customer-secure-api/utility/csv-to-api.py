#!/usr/bin/env python3
import json
import requests
import sys
import os
import pandas as pd

def process_xlsx_via_api(xlsx_file, api_url, api_key):
    """Process XLSX file and insert data via POST API"""
    
    # Get JWT token
    auth_response = requests.post(f"{api_url}/auth", 
                                json={"api_key": api_key})
    if auth_response.status_code != 200:
        print(f"❌ Authentication failed: {auth_response.text}")
        return
    
    token = auth_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Process XLSX
    df = pd.read_excel(xlsx_file)
    
    if len(df.columns) < 2:
        print("❌ XLSX must have at least 2 columns")
        return
    
    processed = 0
    for _, row in df.iterrows():
        if pd.isna(row.iloc[0]) or pd.isna(row.iloc[1]):
            continue
            
        # Create data object with all columns
        data = {}
        for col in df.columns:
            value = row[col]
            if not pd.isna(value):
                data[col] = str(value)
        
        # API payload - use customer_name as mandatory name field
        payload = {
            "name": str(row.iloc[1]),  # customer_name from column 2
            "data": data
        }
            
        # POST to API
        response = requests.post(f"{api_url}/data", 
                               headers=headers, json=payload)
        if response.status_code == 201:
            processed += 1
        else:
            print(f"⚠️  Failed to insert row {processed + 1}: {response.text}")
    
    print(f"✅ Successfully processed {processed} records")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 csv-to-api.py <xlsx-file> <api-url> <api-key>")
        print("Example: python3 csv-to-api.py customers.xlsx https://api.example.com/dev your-api-key")
        sys.exit(1)
    
    xlsx_file = sys.argv[1]
    api_url = sys.argv[2]
    api_key = sys.argv[3]
    
    if not os.path.exists(xlsx_file):
        print(f"❌ XLSX file '{xlsx_file}' not found")
        sys.exit(1)
    
    process_xlsx_via_api(xlsx_file, api_url, api_key)