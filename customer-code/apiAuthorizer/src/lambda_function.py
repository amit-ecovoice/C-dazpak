import json
import boto3
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
auth_table = dynamodb.Table('CustomerDataAuth')

def lambda_handler(event, context):
    logger.info(f"Event: {json.dumps(event)}")
    
    # Extract API key from the Authorization header
    api_key = None
    if 'headers' in event and event.get('headers'):
        auth_header = event.get('headers', {}).get('authorization') or event.get('headers', {}).get('Authorization')
        if auth_header:
            api_key = auth_header
    
    # Extract customer ID from path
    customer_id = None
    path = event.get('rawPath', '')
    path_parts = path.split('/')
    
    # Find customer ID in path - looking for pattern /customers/{customerId}
    for i, part in enumerate(path_parts):
        if part == 'customers' and i + 1 < len(path_parts):
            customer_id = path_parts[i + 1]
            break
    
    logger.info(f"API Key: {api_key}, Customer ID: {customer_id}")
    
    # If we don't have both API key and customer ID, deny access
    if not api_key or not customer_id:
        logger.warning("Missing API key or customer ID")
        return {"isAuthorized": False}
    
    try:
        # Look up the customer's API key in DynamoDB
        response = auth_table.get_item(
            Key={
                'customerId': customer_id,
                'dataId': 'apikey'  # We'll store API keys with dataId = 'apikey'
            }
        )
        
        # Check if the item exists and the API key matches
        if 'Item' in response and response['Item'].get('apiKey') == api_key:
            logger.info(f"Authorization successful for customer: {customer_id}")
            return {
                "isAuthorized": True,
                "context": {
                    "customerId": customer_id
                }
            }
        else:
            logger.warning(f"Invalid API key for customer: {customer_id}")
            return {"isAuthorized": False}
            
    except Exception as e:
        logger.error(f"Error during authorization: {str(e)}")
        return {"isAuthorized": False}
