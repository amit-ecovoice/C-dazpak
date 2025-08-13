import json
import boto3
import secrets
import hashlib
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
secrets_client = boto3.client('secretsmanager')

def lambda_handler(event, context):
    try:
        # Validate admin API key
        if not validate_admin_api_key(event):
            return {
                'statusCode': 401,
                'body': json.dumps({'error': 'Invalid admin API key'}) + '\n'
            }
        
        http_method = event['httpMethod']
        
        if http_method == 'POST':
            return create_api_key(event)
        elif http_method == 'DELETE':
            return revoke_api_key(event)
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

def create_api_key(event):
    body = json.loads(event['body'])
    customer_id = body.get('customer_id')
    customer_name = body.get('customer_name')
    
    if not customer_id or not customer_name:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'customer_id and customer_name required'}) + '\n'
        }
    
    table = dynamodb.Table(os.environ['API_KEYS_TABLE'])
    
    # Check for existing customer_id
    try:
        response = table.scan(
            FilterExpression='customer_id = :cid',
            ExpressionAttributeValues={':cid': customer_id}
        )
        if response['Items']:
            existing_item = response['Items'][0]
            # If API key exists but is inactive, reactivate it
            if not existing_item.get('active', False):
                table.update_item(
                    Key={'api_key_hash': existing_item['api_key_hash']},
                    UpdateExpression='SET active = :active',
                    ExpressionAttributeValues={':active': True}
                )
                # Generate new alphanumeric API key (no symbols)
                api_key = ''.join(secrets.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789') for _ in range(32))
                key_hash = hashlib.sha256(api_key.encode()).hexdigest()
                
                table.update_item(
                    Key={'api_key_hash': existing_item['api_key_hash']},
                    UpdateExpression='SET api_key_hash = :new_hash, active = :active, customer_name = :name',
                    ExpressionAttributeValues={
                        ':new_hash': key_hash,
                        ':active': True,
                        ':name': customer_name
                    }
                )
                
                # Delete old hash entry and create new one
                table.delete_item(Key={'api_key_hash': existing_item['api_key_hash']})
                table.put_item(Item={
                    'api_key_hash': key_hash,
                    'customer_id': customer_id,
                    'customer_name': customer_name,
                    'created_at': datetime.utcnow().isoformat(),
                    'active': True
                })
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'api_key': api_key,
                        'customer_id': customer_id,
                        'message': 'API key reactivated successfully'
                    }) + '\n'
                }
            else:
                # API key exists and is active
                return {
                    'statusCode': 409,
                    'body': json.dumps({'error': f'Active API key for customer ID {customer_id} already exists'}) + '\n'
                }
    except Exception as e:
        print(f"Error checking customer_id: {e}")
    
    # Check for duplicate customer_name (only among active keys)
    try:
        response = table.scan(
            FilterExpression='customer_name = :cname AND active = :active',
            ExpressionAttributeValues={':cname': customer_name, ':active': True}
        )
        if response['Items']:
            return {
                'statusCode': 409,
                'body': json.dumps({'error': f'Customer name "{customer_name}" already exists for an active API key'}) + '\n'
            }
    except Exception as e:
        print(f"Error checking customer_name: {e}")
    
    # Generate secure alphanumeric API key (no symbols)
    api_key = ''.join(secrets.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789') for _ in range(32))
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    # Store in DynamoDB
    table.put_item(Item={
        'api_key_hash': key_hash,
        'customer_id': customer_id,
        'customer_name': customer_name,
        'created_at': datetime.utcnow().isoformat(),
        'active': True
    })
    
    return {
        'statusCode': 201,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'api_key': api_key,
            'customer_id': customer_id,
            'message': 'API key created successfully'
        }) + '\n'
    }

def revoke_api_key(event):
    path_params = event.get('pathParameters') or {}
    customer_id = path_params.get('keyId')
    
    if not customer_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'customer_id required'}) + '\n'
        }
    
    table = dynamodb.Table(os.environ['API_KEYS_TABLE'])
    
    try:
        # Find the API key by customer_id
        response = table.scan(
            FilterExpression='customer_id = :cid',
            ExpressionAttributeValues={':cid': customer_id}
        )
        
        if not response['Items']:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f'API key for customer {customer_id} not found'}) + '\n'
            }
        
        # Mark API key as inactive
        for item in response['Items']:
            table.update_item(
                Key={'api_key_hash': item['api_key_hash']},
                UpdateExpression='SET active = :active',
                ExpressionAttributeValues={':active': False}
            )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': f'API key for customer {customer_id} revoked successfully'
            }) + '\n'
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Failed to revoke API key: {str(e)}'}) + '\n'
        }