# Multi-Tenant API with JWT Authentication

A complete serverless solution for multi-tenant API access with JWT authentication, API key management, and secure data isolation.

## Architecture

- **API Gateway**: Entry point with custom authorizer
- **Lambda Functions**: Auth, authorizer, data API, and key management
- **DynamoDB**: API keys and customer data storage
- **Secrets Manager**: JWT signing secret
- **IAM**: Fine-grained permissions

## Features

- Customer-specific API keys
- JWT token generation and validation
- Lambda authorizer for API Gateway
- Row-level security in DynamoDB
- Complete data isolation between customers

## Data Flow

### Admin Flow

![alt text](image-2.png)



## Deployment

### Prerequisites
- AWS CLI configured with deployment permissions (see below)
- SAM CLI installed
- Python 3.9+

### Required AWS Permissions

To deploy this solution, your AWS user/role must have the following permissions:

#### Core Services
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:CreateStack",
        "cloudformation:UpdateStack",
        "cloudformation:DeleteStack",
        "cloudformation:DescribeStacks",
        "cloudformation:DescribeStackEvents",
        "cloudformation:DescribeStackResources",
        "cloudformation:GetTemplate"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:CreateBucket",
        "s3:DeleteBucket",
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::aws-sam-cli-*",
        "arn:aws:s3:::aws-sam-cli-*/*"
      ]
    }
  ]
}
```

#### Lambda Functions
```json
{
  "Effect": "Allow",
  "Action": [
    "lambda:CreateFunction",
    "lambda:DeleteFunction",
    "lambda:UpdateFunctionCode",
    "lambda:UpdateFunctionConfiguration",
    "lambda:GetFunction",
    "lambda:ListFunctions",
    "lambda:AddPermission",
    "lambda:RemovePermission"
  ],
  "Resource": "*"
}
```

#### API Gateway
```json
{
  "Effect": "Allow",
  "Action": [
    "apigateway:POST",
    "apigateway:GET",
    "apigateway:PUT",
    "apigateway:DELETE",
    "apigateway:PATCH"
  ],
  "Resource": "*"
}
```

#### DynamoDB
```json
{
  "Effect": "Allow",
  "Action": [
    "dynamodb:CreateTable",
    "dynamodb:DeleteTable",
    "dynamodb:DescribeTable",
    "dynamodb:UpdateTable"
  ],
  "Resource": "*"
}
```

#### Secrets Manager
```json
{
  "Effect": "Allow",
  "Action": [
    "secretsmanager:CreateSecret",
    "secretsmanager:DeleteSecret",
    "secretsmanager:DescribeSecret",
    "secretsmanager:GetSecretValue",
    "secretsmanager:UpdateSecret"
  ],
  "Resource": "*"
}
```

#### IAM (for Lambda execution roles)
```json
{
  "Effect": "Allow",
  "Action": [
    "iam:CreateRole",
    "iam:DeleteRole",
    "iam:GetRole",
    "iam:PassRole",
    "iam:AttachRolePolicy",
    "iam:DetachRolePolicy",
    "iam:CreatePolicy",
    "iam:DeletePolicy",
    "iam:GetPolicy"
  ],
  "Resource": "*"
}
```

#### Managed Policy Option
Alternatively, you can use these AWS managed policies:
- `PowerUserAccess` (recommended for development)
- `AdministratorAccess` (full access - use with caution)

#### Minimal Custom Policy
For production deployments, create a custom policy combining all the above permissions or use the SAM deployment policy template.

### Quick Deploy
```bash
# Default deployment
./deploy.sh

# Custom deployment
./deploy.sh --stack-name my-api --region us-west-2 --environment prod --profile my-profile
```

### Parameters
- `--stack-name`: CloudFormation stack name (default: multi-tenant-api)
- `--region`: AWS region (default: us-east-1)
- `--environment`: Environment stage (default: dev)
- `--profile`: AWS profile to use

## Getting Required Parameters

After deployment, you'll need to retrieve the API URL and admin API key:

- **API URL**: Available in CloudFormation stack outputs as `ApiUrl`
- **Admin API Key**: Available in CloudFormation stack outputs as `AdminApiKey` or directly from AWS Secrets Manager secret named `{stack-name}-admin-api-key`
- **Table Names**: Available in CloudFormation outputs as `ApiKeysTableName` and `CustomerDataTableName` (if needed for direct database access)

Use the AWS CLI `describe-stacks` command to view all outputs, or retrieve the admin key directly from Secrets Manager using `get-secret-value`.

## API Endpoints

### Setup Environment Variables
```bash
# Set API URL from CloudFormation output
export API_URL=<ApiUrl>

# Set Admin API Key from CloudFormation output
export ADMIN_API_KEY=<AdminApiKey>

# Verify setup
echo "API URL: $API_URL"
echo "Admin API Key: $ADMIN_API_KEY"
```

### 1. Create API Key (Admin API Key Required)
```bash
curl -X POST "$API_URL/admin/keys" -H "Content-Type: application/json" -H "X-Admin-API-Key: $ADMIN_API_KEY" -d '{"customer_id":"customer-123","customer_name":"Customer Name"}'
```
**Response:**
```json
{"api_key": "YAHA3DePs-MOPpMq3_xZG8lUYeT3SSm8fTFz3sczXVk", "customer_id": "customer-123", "message": "API key created successfully"}
```

### 2. Get JWT Token
```bash
curl -X POST "$API_URL/auth" -H "Content-Type: application/json" -d '{"api_key":"your-api-key"}'
```
**Response:**
```json
{"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjdXN0b21lcl9pZCI6InRlc3QtY3VzdG9tZXItMSIsImV4cCI6MTc1NDMzNjcxOCwiaWF0IjoxNzU0MzMzMTE4fQ.LoZn3BLXJDoIhrhhvNQUFTSuPhTm7GxIUP8KCXUyePw", "expires_in": 3600}
```

### 3. Access Data (GET)
```bash
# Get all data
curl -X GET "$API_URL/data" -H "Authorization: Bearer $TOKEN"
```
**Response:**
```json
{"customer_id": "test-customer-1", "data": [{"customer_id": "test-customer-1", "value": 10.0, "data_id": "sample-data-1", "created_at": "2025-08-04T18:44:46Z", "name": "Sample Data Item 1"}], "count": 1}
```

```bash
# Get paginated data
curl -X GET "$API_URL/data?limit=2" -H "Authorization: Bearer $TOKEN"
```
**Response:**
```json
{"customer_id": "test-customer-1", "data": [{"customer_id": "test-customer-1", "value": 10.0, "data_id": "sample-data-1", "created_at": "2025-08-04T18:44:46Z", "name": "Sample Data Item 1"}, {"customer_id": "test-customer-1", "value": 20.0, "data_id": "sample-data-2", "created_at": "2025-08-04T18:51:31Z", "name": "Sample Data Item 2"}], "count": 2, "nextToken": "eyJjdXN0b21lcl9pZCI6ICJ0ZXN0LWN1c3RvbWVyLTEiLCAiZGF0YV9pZCI6ICJzYW1wbGUtZGF0YS0yIn0="}
```

### 4. Create Data (POST)
```bash
curl -X POST "$API_URL/data" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"name":"My Data Item","value":100,"description":"Custom field"}'
```
**Response:**
```json
{"message": "Data created successfully", "item": {"customer_id": "test-customer-1", "data_id": "2fe7d451-05c6-42e5-bf9b-5d8fddf940f7", "name": "My Data Item", "value": 100, "created_at": "2025-08-04T19:09:56.473428Z", "description": "Custom field"}}
```

### 5. Delete API Key
```bash
curl -X DELETE "$API_URL/admin/keys/customer-123" -H "Content-Type: application/json" -H "X-Admin-API-Key: $ADMIN_API_KEY"
```
**Response:**
```json
{"message": "API key for customer customer-123 revoked"}
```



## Authentication Methods

| Endpoint | Auth Method | Required Header/Credential |
|----------|-------------|----------------------------|
| `/admin/keys` | Admin API Key | `X-Admin-API-Key: <admin-key>` |
| `/auth` | API Key | `api_key` in request body |
| `/data` | JWT Token | `Authorization: Bearer <token>` |

## Security Features

- **API keys**: Hashed before storage using SHA-256
- **JWT tokens**: Expire after 1 hour, signed with HS256
- **Customer isolation**: Row-level security in DynamoDB
- **Admin endpoints**: Protected by admin API key authentication
- **CORS**: Enabled for web applications
- **Audit trail**: All API calls logged to CloudWatch

## Monitoring

- CloudWatch logs for all Lambda functions
- DynamoDB metrics
- API Gateway access logs
- Custom metrics for API usage

## Error Responses

```bash
# Invalid API key
# HTTP 401
{"error": "Invalid API key"}

# Expired JWT token
# HTTP 401
{"message": "Unauthorized: Token expired"}

# Missing IAM permissions
# HTTP 403
{"message": "User is not authorized to perform this operation"}
```

## Cleanup

```bash
# Delete CloudFormation stack
aws cloudformation delete-stack --stack-name multi-tenant-api

# Or with custom stack name
aws cloudformation delete-stack --stack-name your-stack-name
```