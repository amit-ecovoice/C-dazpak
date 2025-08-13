import json
import boto3
import os
from datetime import datetime
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
secrets_client = boto3.client('secretsmanager')

# Custom JSON encoder for Decimal types
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    try:
        # Validate admin API key
        if not validate_admin_api_key(event):
            return {
                'statusCode': 401,
                'body': json.dumps({'error': 'Invalid admin API key'}) + '\n'
            }
        
        http_method = event['httpMethod']
        
        if http_method == 'PUT':
            return upsert_data(event)
        else:
            return {
                'statusCode': 405,
                'body': json.dumps({'error': 'Method not allowed'}) + '\n'
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}) + '\n'
        }

def validate_admin_api_key(event):
    try:
        # Get admin API key from header
        headers = event.get('headers', {})
        provided_key = headers.get('X-Admin-API-Key') or headers.get('x-admin-api-key')
        
        if not provided_key:
            return False
        
        # Get admin API key from secrets manager
        secret_response = secrets_client.get_secret_value(
            SecretId=os.environ['ADMIN_API_KEY_SECRET']
        )
        admin_key = json.loads(secret_response['SecretString'])['admin_api_key']
        
        return provided_key == admin_key
    except Exception:
        return False

def upsert_data(event):
    body = json.loads(event['body'])
    customer_id = body.get('customer_id')
    data_id = body.get('data_id')
    data = body.get('data', {})
    
    if not customer_id or not data_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'customer_id and data_id are required'}) + '\n'
        }
    
    table = dynamodb.Table(os.environ['CUSTOMER_DATA_TABLE'])
    
    # Prepare item for upsert
    item = {
        'customer_id': customer_id,
        'data_id': data_id,
        'updated_at': datetime.utcnow().isoformat() + 'Z'
    }
    
    # Add all data fields
    for key, value in data.items():
        item[key] = value
    
    # Add created_at only if it's a new item
    try:
        existing_item = table.get_item(
            Key={'customer_id': customer_id, 'data_id': data_id}
        )
        if 'Item' not in existing_item:
            item['created_at'] = datetime.utcnow().isoformat() + 'Z'
    except Exception:
        item['created_at'] = datetime.utcnow().isoformat() + 'Z'
    
    # Upsert the item
    table.put_item(Item=item)
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'message': 'Data upserted successfully',
            'item': item
        }, cls=DecimalEncoder) + '\n'
    }