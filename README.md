**Structure**
├── Indexing/hubspot_deals.py                # Fetches and processes deal data from HubSpot\n
│   └── **Purpose:** Connects to the HubSpot API, retrieves deal data, transforms it into JSON format, and saves it for further processing.\n
│
├── Indexing/lambda_function_hubspotdeals.py              # Processes deal files from S3 and indexes them in Glean
│   └── **Purpose:** Listens for S3 events, parses deal object files, creates document payloads, sends them to the Glean API, and moves processed files to a `processed/` folder.
│
├── Indexing/glean-bulk-index-stack.yaml     # CloudFormation template for bulk indexing infrastructure
│   └── **Purpose:** Provisions an S3 bucket, Lambda function, and event triggers to automate the bulk indexing workflow.
│
├── Indexing/deploy_bulkindex.sh             # Automates deployment of bulk indexing infrastructure
│   └── **Purpose:** Deploys the `glean-bulk-index-stack.yaml` template using AWS CLI and sets up the required environment.
│
├── Search/glean_chatbot_app.py            # Streamlit-based chatbot application for searching indexed documents
│   └── **Purpose:** Provides a web interface for users to search and interact with indexed documents via the Glean API.
│
├── Search/ec2-streamlit-stack.yaml        # CloudFormation template for Streamlit app infrastructure
│   └── **Purpose:** Provisions an EC2 instance and related resources to host the Streamlit chatbot application.
│
├── Search/deploy_search.sh                # Automates deployment of the Streamlit chatbot application
│   └── **Purpose:** Installs dependencies, copies application files to the EC2 instance, and starts the Streamlit application.
│
├── Search/stop_streamlit.sh               # Stops the Streamlit chatbot application
│   └── **Purpose:** Terminates the Streamlit process running on the EC2 instance to free up resources or prepare for updates.


**Indexing**- This folder contains code to Index documents into Glean Custom Data Source.

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

**Overall Workflow:**
Data Fetching: Use hubspot_deals.py to fetch and save deal data from the HubSpot API.
File Upload: Upload the deal object files to the deals/ folder in the S3 bucket.
File Processing: The lambda_function_hubspotdeals.py processes the uploaded files, prepares them for indexing, and sends them to the Glean API.
Infrastructure Deployment: Use glean-bulk-index-stack.yaml and deploy_bulkindex.sh to set up and manage the required AWS infrastructure.
This setup ensures a seamless pipeline for fetching, processing, and indexing deal data into Glean.



**Search** - This folder contains code to search Glean Index

1. glean_chatbot_app.py
Purpose:
This script implements a chatbot application using Streamlit to provide a user-friendly interface for searching and interacting with indexed documents in Glean.

Key Features:
Streamlit Integration: Provides a web-based interface for users to input search queries and view results.
Glean API Integration: Connects to the Glean search API to fetch search results based on user queries.
Interactive Chatbot: Allows users to interact with the application in a conversational manner, refining their searches or exploring related documents.
Search Result Display: Displays search results in a structured format, including document titles, summaries, and links.
Typical Workflow:
User enters a search query in the Streamlit interface.
The app sends the query to the Glean search API.
The API returns relevant search results.
The app displays the results, allowing users to explore further.

2. ec2-streamlit-stack.yaml
Purpose:
This AWS CloudFormation template is used to deploy the infrastructure required to host the Streamlit-based chatbot application on an EC2 instance.

Key Features:
EC2 Instance Creation: Provisions an EC2 instance to host the Streamlit application.
Security Group Configuration: Configures security groups to allow HTTP/HTTPS traffic to the instance.
IAM Role Setup: Sets up IAM roles and permissions for the EC2 instance to access necessary AWS resources.
Elastic IP Association: Optionally associates an Elastic IP with the EC2 instance for consistent access.
Typical Workflow:
Define the infrastructure as code in the YAML file.
Deploy the stack using AWS CloudFormation.
The stack provisions the EC2 instance and configures it to host the Streamlit application.
The application is accessible via the public IP or domain associated with the EC2 instance.

3. deploy_search.sh
Purpose:
This shell script automates the deployment of the Streamlit-based chatbot application on the EC2 instance.

Key Features:
Application Deployment: Copies the glean_chatbot_app.py script and other necessary files to the EC2 instance.
Environment Setup: Installs required dependencies (e.g., Python, Streamlit, libraries) on the EC2 instance.
Streamlit Launch: Starts the Streamlit application on the EC2 instance, making it accessible to users.
Typical Workflow:
Run the script from the command line.
The script connects to the EC2 instance via SSH.
Installs dependencies and copies application files.
Launches the Streamlit application.

4. stop_streamlit.sh
Purpose:
This shell script stops the Streamlit application running on the EC2 instance.

Key Features:
Process Termination: Identifies and terminates the Streamlit process running on the EC2 instance.
Resource Management: Ensures that the application is stopped to free up resources or prepare for updates.
Typical Workflow:
Run the script from the command line.
The script connects to the EC2 instance via SSH.
Identifies the Streamlit process and terminates it.
Confirms that the application has been stopped.

**Overall Workflow:**
Infrastructure Deployment: Use ec2-streamlit-stack.yaml to provision the EC2 instance and related resources.
Application Deployment: Use deploy_search.sh to set up and launch the Streamlit-based chatbot application.
Search Interaction: Users interact with the chatbot via the Streamlit interface to perform searches and view results.
Application Management: Use stop_streamlit.sh to stop the application when needed.
This setup provides a scalable and user-friendly solution for searching and interacting with indexed documents in Glean.


