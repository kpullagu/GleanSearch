#!/bin/bash

# Set your variables
STACK_NAME="streamlit-app-stack"
KEY_PAIR_NAME="ec2-streamlit-key"  # Replace with your key pair name
SECRET_NAME="glean-api-secret"  # Replace with your actual secret name

# Deploy the CloudFormation stack
aws cloudformation create-stack \
  --stack-name $STACK_NAME \
  --template-body file://ec2-streamlit-stack.yaml \
  --parameters ParameterKey=KeyName,ParameterValue=$KEY_PAIR_NAME \
               ParameterKey=SecretName,ParameterValue=$SECRET_NAME \
  --capabilities CAPABILITY_IAM

# Wait for stack creation to complete
echo "Waiting for stack creation to complete..."
aws cloudformation wait stack-create-complete --stack-name $STACK_NAME

# Get the outputs
echo "Stack creation completed. Outputs:"
aws cloudformation describe-stacks --stack-name $STACK_NAME --query 'Stacks[0].Outputs'
