#!/bin/bash

# Multi-tenant API deployment script



# Configuration
export STACK_NAME="multi-tenant-api"
export REGION="us-east-1"
export ENVIRONMENT="dev"
export PROFILE="default"


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
echo "Deleting SAM application..."
sam delete --stack-name $STACK_NAME --region $REGION --profile $PROFILE --no-prompts




