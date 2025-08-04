import json
import boto3
import os
from boto3.dynamodb.conditions import Key
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')

# Custom JSON encoder for Decimal types
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    try:
        # Get customer ID from authorizer context
        customer_id = event['requestContext']['authorizer']['customerId']
        http_method = event['httpMethod']
        
        if http_method == 'GET':
            return get_data(customer_id, event)
        elif http_method == 'POST':
            return post_data(customer_id, event)
        else:
            return {
                'statusCode': 405,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Method not allowed'}) + '\n'
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)}) + '\n'
        }

def get_data(customer_id, event):
    # Get query parameters
    query_params = event.get('queryStringParameters') or {}
    limit = int(query_params.get('limit', 50))  # Default 50 items per page
    next_token = query_params.get('nextToken')
    
    # Query DynamoDB with customer isolation
    table = dynamodb.Table(os.environ['CUSTOMER_DATA_TABLE'])
        
    query_kwargs = {
        'KeyConditionExpression': Key('customer_id').eq(customer_id),
        'Limit': limit
    }
    
    # Add pagination token if provided
    if next_token:
        try:
            import base64
            exclusive_start_key = json.loads(base64.b64decode(next_token).decode())
            query_kwargs['ExclusiveStartKey'] = exclusive_start_key
        except Exception:
            pass  # Invalid token, ignore
    
    response = table.query(**query_kwargs)
    
    # Prepare response
    result = {
        'customer_id': customer_id,
        'data': response['Items'],
        'count': response['Count']
    }
    
    # Add next token if more data available
    if 'LastEvaluatedKey' in response:
        import base64
        next_token = base64.b64encode(
            json.dumps(response['LastEvaluatedKey']).encode()
        ).decode()
        result['nextToken'] = next_token
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(result, cls=DecimalEncoder) + '\n'
    }

def post_data(customer_id, event):
    from datetime import datetime
    import uuid
    
    # Parse request body
    body = json.loads(event['body'])
    
    # Validate required fields
    if 'name' not in body:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'name field is required'}) + '\n'
        }
    
    # Prepare item for insertion
    table = dynamodb.Table(os.environ['CUSTOMER_DATA_TABLE'])
    
    item = {
        'customer_id': customer_id,
        'data_id': body.get('data_id', str(uuid.uuid4())),
        'name': body['name'],
        'value': body.get('value', 0),
        'created_at': datetime.utcnow().isoformat() + 'Z'
    }
    
    # Add any additional fields from request
    for key, value in body.items():
        if key not in ['customer_id', 'data_id', 'name', 'value', 'created_at']:
            item[key] = value
    
    # Insert item
    table.put_item(Item=item)
    
    return {
        'statusCode': 201,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'message': 'Data created successfully',
            'item': item
        }, cls=DecimalEncoder) + '\n'
    }