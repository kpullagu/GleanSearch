Structure:

Indexing - This folder contains code to Index documents into Glean Custom Data Source.

Search - This folder contains code to search Glean Index

1. hubspot_deals.py
Purpose:
This script is responsible for fetching deal data from the HubSpot API and preparing it for further processing. It extracts deal information and saves it in a structured format (e.g., JSON) for downstream indexing.

Key Features:
HubSpot API Integration: Connects to the HubSpot API using an API key or OAuth token to retrieve deal data.
Data Transformation: Processes the raw deal data into a structured format, including fields like dealname, amount, pipeline, and dealstage.
File Output: Saves the transformed deal data as JSON files in a specified directory for further processing by other scripts.
Save the data as JSON files in a local directory or upload it to an S3 bucket.


2. lambda_function_hubspotdeals.py
Purpose:
This AWS Lambda function processes deal object files stored in an S3 bucket, prepares them for indexing, and sends them to the Glean bulk indexing API.

Key Features:
S3 Integration: Listens for S3 events to detect new deal object files in the deals/ folder.
File Parsing: Reads and parses the deal object files to extract metadata and content.
Document Creation: Maps the parsed data to a document payload structure compatible with the Glean API.
Bulk Indexing: Sends the prepared documents to the Glean bulk indexing API for indexing.
File Management: Moves successfully processed files to a processed/ folder in the same S3 bucket.
Typical Workflow:
Triggered by an S3 event when a new file is uploaded to the deals/ folder.
Reads the file content and parses it to extract relevant fields (e.g., dealname, amount, pipeline).
Creates a document payload for each file.
Sends the documents to the Glean API for indexing.
Moves successfully processed files to the processed/ folder.

3. glean-bulk-index-stack.yaml
Purpose:
This is an AWS CloudFormation template used to deploy the infrastructure required for the bulk indexing process.

Key Features:
S3 Bucket Creation: Creates an S3 bucket to store deal object files.
Lambda Function Deployment: Deploys the lambda_function_hubspotdeals.py as an AWS Lambda function.
Event Trigger Configuration: Configures the S3 bucket to trigger the Lambda function on file uploads.
IAM Roles and Policies: Sets up the necessary IAM roles and permissions for the Lambda function to access S3 and other AWS services.
Typical Workflow:
Define the infrastructure as code in the YAML file.
Deploy the stack using AWS CloudFormation.
The stack creates the S3 bucket, Lambda function, and event triggers.
The deployed infrastructure is ready to process deal object files.

4. deploy_bulkindex.sh
Purpose:
This shell script automates the deployment of the bulk indexing infrastructure using the CloudFormation template.

Key Features:
CloudFormation Deployment: Uses the AWS CLI to deploy the glean-bulk-index-stack.yaml template.
Environment Configuration: Sets up environment variables required for the deployment (e.g., stack name, S3 bucket name).
Error Handling: Includes checks to ensure the deployment is successful and provides feedback in case of errors.
Typical Workflow:
Run the script from the command line.
The script sets up the required environment variables.
Deploys the CloudFormation stack using the AWS CLI.
Outputs the status of the deployment and any relevant resource details.

Overall Workflow:
Data Fetching: Use hubspot_deals.py to fetch and save deal data from the HubSpot API.
File Upload: Upload the deal object files to the deals/ folder in the S3 bucket.
File Processing: The lambda_function_hubspotdeals.py processes the uploaded files, prepares them for indexing, and sends them to the Glean API.
Infrastructure Deployment: Use glean-bulk-index-stack.yaml and deploy_bulkindex.sh to set up and manage the required AWS infrastructure.
This setup ensures a seamless pipeline for fetching, processing, and indexing deal data into Glean.
