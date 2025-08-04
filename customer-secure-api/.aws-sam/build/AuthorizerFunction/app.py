import json
import jwt
import boto3
import os

secrets_client = boto3.client('secretsmanager')

def lambda_handler(event, context):
    token = event['authorizationToken']
    
    if token.startswith('Bearer '):
        token = token[7:]
    
    try:
        # Get JWT secret
        secret_response = secrets_client.get_secret_value(
            SecretId=os.environ['JWT_SECRET_NAME']
        )
        secret = json.loads(secret_response['SecretString'])['secret']
        
        # Decode JWT
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        customer_id = payload['customer_id']
        
        # Generate policy
        policy = generate_policy(customer_id, 'Allow', event['methodArn'])
        policy['context'] = {
            'customerId': customer_id
        }
        
        return policy
        
    except jwt.ExpiredSignatureError:
        raise Exception('Unauthorized: Token expired')
    except jwt.InvalidTokenError:
        raise Exception('Unauthorized: Invalid token')
    except Exception as e:
        raise Exception(f'Unauthorized: {str(e)}')

def generate_policy(principal_id, effect, resource):
    return {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'execute-api:Invoke',
                'Effect': effect,
                'Resource': resource
            }]
        }
    }