import json
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
auth_table = dynamodb.Table('CustomerDataAuth')
data_table = dynamodb.Table('CustomerData')

def lambda_handler(event, context):
    try:
        # Debug: Print the entire event information
        print(f"Full event: {json.dumps(event)}")
        
        # Extract customer from path parameters
        path_params = event.get('pathParameters', {})
        customer_name = path_params.get('customerId') if path_params else None
        
        # Extract apiKey from Authorization header
        headers = event.get('headers', {})
        api_key = headers.get('Authorization') or headers.get('authorization')
        
        # Debug: Print extracted values
        print(f"Path parameters: {path_params}")
        print(f"Headers: {headers}")
        print(f"Extracted customer_name: {customer_name}")
        print(f"Extracted api_key: {api_key}")
        
        # Remove 'Bearer ' prefix if present
        if api_key and api_key.startswith('Bearer '):
            api_key = api_key[7:]
        
        print(f"Final - Customer: {customer_name}, API Key: {api_key}")
        
        # Validate required parameters
        if not customer_name or not api_key:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'Customer name and API key are required',
                    'debug': {
                        'customer_name': customer_name,
                        'api_key_present': bool(api_key),
                        'path_params': path_params,
                        'headers_keys': list(headers.keys()) if headers else []
                    }
                })
            }
        
        # Query all records for the customer using GSI
        all_items = []
        last_evaluated_key = None
        
        while True:
            query_params = {
                'IndexName': 'CustomerIndex',  # Make sure this GSI exists
                'KeyConditionExpression': Key('Customer').eq(customer_name)
            }
            
            # Add pagination key if exists
            if last_evaluated_key:
                query_params['ExclusiveStartKey'] = last_evaluated_key
            
            response = data_table.query(**query_params)
            
            # Add items to our collection
            all_items.extend(response.get('Items', []))
            
            # Check if there are more items to fetch
            last_evaluated_key = response.get('LastEvaluatedKey')
            if not last_evaluated_key:
                break
        
        print(f"Found {len(all_items)} items for customer {customer_name}")
        
        # Return all items
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(all_items, default=str)  # default=str handles datetime objects
        }
        
    except ClientError as e:
        print(f"DynamoDB error: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'message': 'Error querying database', 'error': str(e)})
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'message': 'Internal server error', 'error': str(e)})
        }
