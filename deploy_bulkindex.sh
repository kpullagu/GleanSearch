#!/bin/bash

# -----------------------------
# Configuration Variables
# -----------------------------
STACK_NAME="glean-stack"
TEMPLATE_FILE="glean-bulk-index-stack.yaml"
REGION="us-east-1"  # Change this to your AWS region

# Glean Configuration
LAMBDA_FUNCTION_NAME="s3-sqs-glean-indexer "  # Your existing Lambda function name
GLEAN_API_TOKEN="y1ica8IKPeiKjQBPtu99uVyKpl820DE3B9vw7yq1FIM="
GLEAN_DATASOURCE="interviewds"
GLEAN_API_ENDPOINT="https://glean-be.glean.com/api/index/v1/bulkindexdocuments"

# -----------------------------
# Functions
# -----------------------------

# Delete existing stack if it exists
echo "Checking for existing stack..."
if aws cloudformation describe-stacks --stack-name $STACK_NAME 2>/dev/null; then
    echo "Deleting existing stack..."
    aws cloudformation delete-stack --stack-name $STACK_NAME
    echo "Waiting for stack deletion..."
    aws cloudformation wait stack-delete-complete --stack-name $STACK_NAME
fi

# Deploy new stack
echo "Deploying new stack..."
aws cloudformation create-stack \
    --stack-name $STACK_NAME \
    --template-body file://$TEMPLATE_FILE \
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
    --parameters \
        ParameterKey=LambdaFunctionName,ParameterValue=$LAMBDA_FUNCTION_NAME \
        ParameterKey=GleanApiToken,ParameterValue=$GLEAN_API_TOKEN \
        ParameterKey=GleanDatasource,ParameterValue=$GLEAN_DATASOURCE \
        ParameterKey=GleanApiEndpoint,ParameterValue=$GLEAN_API_ENDPOINT \
    --region $REGION

echo "Waiting for stack creation to complete..."
aws cloudformation wait stack-create-complete --stack-name $STACK_NAME

echo "Stack deployment completed!"

# Print outputs
echo "Stack Outputs:"
aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs' \
    --output table
