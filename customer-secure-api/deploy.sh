#!/bin/bash

# Multi-tenant API deployment script



# Configuration
export STACK_NAME="multi-tenant-api"
export REGION="us-east-1"
export ENVIRONMENT="dev"
export PROFILE="ecov"


echo "=== Multi-tenant API Deployment ==="
echo "Stack Name: $STACK_NAME"
echo "Region: $REGION"
echo "Environment: $ENVIRONMENT"


# Check if SAM CLI is installed
if ! command -v sam &> /dev/null; then
    echo "Error: SAM CLI is not installed. Please install it first."
    echo "Visit: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html"
    exit 1
fi

# Build the application
echo "Building SAM application..."
sam build

# Deploy the application
echo "Deploying SAM application..."

sam deploy --stack-name $STACK_NAME --region $REGION --parameter-overrides Environment=$ENVIRONMENT --capabilities CAPABILITY_NAMED_IAM --confirm-changeset --resolve-s3 --profile $PROFILE


