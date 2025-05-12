**Structure**
# Project Structure

```bash
Project Structure
├── Indexing/
│   ├── hubspot_deals.py
│   │   └── Purpose: Connects to the HubSpot API, retrieves deal data, transforms it into JSON format, and saves it for further processing.
│   │
│   ├── lambda_function_hubspotdeals.py
│   │   └── Purpose: Listens for S3 events, parses deal object files, creates document payloads, sends them to the Glean API, and moves processed files to a processed/ folder.
│   │
│   ├── glean-bulk-index-stack.yaml
│   │   └── Purpose: Provisions an S3 bucket, Lambda function, and event triggers to automate the bulk indexing workflow.
│   │
│   └── deploy_bulkindex.sh
│       └── Purpose: Deploys the glean-bulk-index-stack.yaml template using AWS CLI and sets up the required environment.
│
└── Search/
    ├── glean_chatbot_app.py
    │   └── Purpose: Provides a web interface for users to search and interact with indexed documents via the Glean API.
    │
    ├── ec2-streamlit-stack.yaml
    │   └── Purpose: Provisions an EC2 instance and related resources to host the Streamlit chatbot application.
    │
    ├── deploy_search.sh
    │   └── Purpose: Installs dependencies, copies application files to the EC2 instance, and starts the Streamlit application.
    │
    └── stop_streamlit.sh
        └── Purpose: Terminates the Streamlit process running on the EC2 instance to free up resources or prepare for updates.


Detailed Description
Indexing Folder
hubspot_deals.py

    Purpose: This script is responsible for fetching deal data from the HubSpot API and preparing it for further processing.
    Key Features:
        HubSpot API Integration: Connects to the HubSpot API using an API key or OAuth token to retrieve deal data.
        Data Transformation: Processes the raw deal data into a structured format, including fields like dealname, amount, pipeline, and dealstage.
        File Output: Saves the transformed deal data as JSON files in a specified directory for further processing by other scripts.

lambda_function_hubspotdeals.py

    Purpose: AWS Lambda function that processes deal object files from S3 and indexes them in Glean
    Key Features:
        S3 Integration: Listens for S3 events to detect new deal object files in the deals/ folder.
        File Parsing: Reads and parses the deal object files to extract metadata and content.
        Document Creation: Maps the parsed data to a document payload structure compatible with the Glean API.
        Bulk Indexing: Sends the prepared documents to the Glean bulk indexing API for indexing.
        File Management: Moves successfully processed files to a processed/ folder in the same S3 bucket.

glean-bulk-index-stack.yaml

    Purpose: CloudFormation template for bulk indexing infrastructure
    Key Features:
        S3 Bucket Creation: Creates an S3 bucket to store deal object files.
        Lambda Function Deployment: Deploys the lambda_function_hubspotdeals.py as an AWS Lambda function.
        Event Trigger Configuration: Configures the S3 bucket to trigger the Lambda function on file uploads.
        IAM Roles and Policies: Sets up the necessary IAM roles and permissions for the Lambda function to access S3 and other AWS services.

deploy_bulkindex.sh

    Purpose: Automates deployment of bulk indexing infrastructure
    Key Features:
        CloudFormation Deployment: Uses the AWS CLI to deploy the glean-bulk-index-stack.yaml template.
        Environment Configuration: Sets up environment variables required for the deployment (e.g., stack name, S3 bucket name).
        Error Handling: Includes checks to ensure the deployment is successful and provides feedback in case of errors.

Search Folder
glean_chatbot_app.py

    Purpose: Streamlit-based chatbot application for searching indexed documents
    Key Features:
        Streamlit Integration: Provides a web-based interface for users to input search queries and view results.
        Glean API Integration: Connects to the Glean search API to fetch search results based on user queries.
        Interactive Chatbot: Allows users to interact with the application in a conversational manner, refining their searches or exploring related documents.
        Search Result Display: Displays search results in a structured format, including document titles, summaries, and links.

ec2-streamlit-stack.yaml

    Purpose: CloudFormation template for Streamlit app infrastructure
    Key Features:
        EC2 Instance Creation: Provisions an EC2 instance to host the Streamlit application.
        Security Group Configuration: Configures security groups to allow HTTP/HTTPS traffic to the instance.
        IAM Role Setup: Sets up IAM roles and permissions for the EC2 instance to access necessary AWS resources.
        Elastic IP Association: Optionally associates an Elastic IP with the EC2 instance for consistent access.

deploy_search.sh

    Purpose: Automates deployment of the Streamlit chatbot application
    Key Features:
        Application Deployment: Copies the glean_chatbot_app.py script and other necessary files to the EC2 instance.
        Environment Setup: Installs required dependencies (e.g., Python, Streamlit, libraries) on the EC2 instance.
        Streamlit Launch: Starts the Streamlit application on the EC2 instance, making it accessible to users.

stop_streamlit.sh

    Purpose: Stops the Streamlit chatbot application
    Key Features:
        Process Termination: Identifies and terminates the Streamlit process running on the EC2 instance.
        Resource Management: Ensures that the application is stopped to free up resources or prepare for updates.

Overall Workflow
Indexing Process

    Use hubspot_deals.py to fetch and save deal data from the HubSpot API.
    Upload the deal object files to the deals/ folder in the S3 bucket.
    The lambda_function_hubspotdeals.py processes the uploaded files, prepares them for indexing, and sends them to the Glean API.
    Use glean-bulk-index-stack.yaml and deploy_bulkindex.sh to set up and manage the required AWS infrastructure.

Search Implementation

    Use ec2-streamlit-stack.yaml to provision the EC2 instance and related resources.
    Use deploy_search.sh to set up and launch the Streamlit-based chatbot application.
    Users interact with the chatbot via the Streamlit interface to perform searches and view results.
    Use stop_streamlit.sh to stop the application when needed.

This setup ensures a seamless pipeline for fetching, processing, and indexing deal data into Glean, as well as providing a user-friendly search interface for accessing the indexed information.


