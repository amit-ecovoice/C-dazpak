import json
import boto3
import jwt
import hashlib
import os
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb')
secrets_client = boto3.client('secretsmanager')

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        api_key = body.get('api_key')
        
        if not api_key:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'API key required'}) + '\n'
            }
        
        # Validate API key
        customer_id = validate_api_key(api_key)
        
        if not customer_id:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': 'Invalid API key'}) + '\n'
            }
        
        # Generate JWT
        token = generate_jwt(customer_id)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'token': token,
                'expires_in': 3600
            }) + '\n'
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}) + '\n'
        }

def validate_api_key(api_key):
    table = dynamodb.Table(os.environ['API_KEYS_TABLE'])
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    try:
        response = table.get_item(Key={'api_key_hash': key_hash})
        item = response.get('Item')
        
        if item and item.get('active', False):
            return item['customer_id']
    except Exception:
        pass
    
    return None

def generate_jwt(customer_id):
    # Get JWT secret
    secret_response = secrets_client.get_secret_value(
        SecretId=os.environ['JWT_SECRET_NAME']
    )
    secret = json.loads(secret_response['SecretString'])['secret']
    
    payload = {
        'customer_id': customer_id,
        'exp': datetime.utcnow() + timedelta(hours=1),
        'iat': datetime.utcnow()
    }
    
    return jwt.encode(payload, secret, algorithm='HS256')