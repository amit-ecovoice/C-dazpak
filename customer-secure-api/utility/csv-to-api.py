#!/usr/bin/env python3
import json
import requests
import sys
import os
import pandas as pd

def process_xlsx_via_upsert(xlsx_file, api_url, admin_api_key):
    """Process XLSX file and upsert data via admin endpoint"""
    
    headers = {
        "X-Admin-API-Key": admin_api_key,
        "Content-Type": "application/json"
    }
    
    # Process XLSX
    df = pd.read_excel(xlsx_file)
    print(f"📄 Processing {len(df)} records from {xlsx_file}")
    print(f"📄 Columns: {df.columns}")
    # Check for required columns
    required_cols = ['Customer', 'SONum', 'SOLine']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"❌ Missing required columns: {missing_cols}")
        return
    
    processed = 0
    for _, row in df.iterrows():
        if pd.isna(row['Customer']) or pd.isna(row['SONum']) or pd.isna(row['SOLine']):
            continue
            
        # Create customer_id from Customer column
        customer_id = str(row['Customer'])
        
        # Create data_id from SONum + SOLine
        data_id = f"{row['SONum']}-{row['SOLine']}"
        
        # Create data object with all columns except Customer, SONum, SOLine
        data = {}
        for col in df.columns:
            if col not in ['Customer', 'SONum', 'SOLine']:
                value = row[col]
                if not pd.isna(value):
                    data[col] = str(value)
        
        # Add SONum and SOLine to data for reference
        data['SONum'] = str(row['SONum'])
        data['SOLine'] = str(row['SOLine'])
        
        # API payload for upsert
        payload = {
            "customer_id": customer_id,
            "data_id": data_id,
            "data": data
        }
            
        # PUT to admin upsert endpoint
        response = requests.put(f"{api_url}/admin/upsert", 
                               headers=headers, json=payload)
        if response.status_code == 200:
            processed += 1
        else:
            print(f"⚠️  Failed to upsert row {processed + 1}: {response.text}")
    
    print(f"✅ Successfully processed {processed} records")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 csv-to-api.py <xlsx-file> <api-url> <admin-api-key>")
        print("Example: python3 csv-to-api.py Calyx20250804.xlsx https://api.example.com/dev your-admin-api-key")
        sys.exit(1)
    
    xlsx_file = sys.argv[1]
    api_url = sys.argv[2]
    admin_api_key = sys.argv[3]
    
    if not os.path.exists(xlsx_file):
        print(f"❌ XLSX file '{xlsx_file}' not found")
        sys.exit(1)
    
    process_xlsx_via_upsert(xlsx_file, api_url, admin_api_key)