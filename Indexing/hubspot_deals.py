import os
import json
import random
from datetime import datetime, timedelta

# Create the folder if it doesn't exist
folder_name = "sample_folder_deals"
os.makedirs(folder_name, exist_ok=True)

# Starting random number for deal IDs
start_id = random.randint(1, 20000)

# List of random email addresses for the owner field
owner_emails = [
    "alex@example.com",
    "john.doe@example.com",
    "jane.smith@example.com",
    "alice.johnson@example.com",
    "sales.team@example.com"
]

# Function to generate a deal payload based on the sample structure
def generate_deal_payload(deal_id, event_type):
    timestamp = datetime.now().isoformat()
    created_date = (datetime.now() - timedelta(days=30)).isoformat()
    last_modified_date = datetime.now().isoformat()
    
    return {
        "objectId": deal_id,
        "eventType": event_type,
        "timestamp": timestamp,
        "properties": {
            "dealname": f"Sample Deal {deal_id}",
            "amount": str(round(random.uniform(1000, 50000), 2)),
            "dealstage": random.choice(["appointmentscheduled", "qualifiedtobuy", "decisionmakerboughtin"]),
            "pipeline": "default",
            "hubspot_owner_id": random.choice(owner_emails),
            "createdate": created_date,
            "hs_lastmodifieddate": last_modified_date
        }
    }

# Generate deals
num_deals = 1000 # Number of deals to generate
current_id = start_id

for i in range(num_deals):
    # Generate "CREATED" deal
    created_deal_payload = generate_deal_payload(current_id, "CREATED")
    created_deal_filename = os.path.join(folder_name, f"deal_created_{current_id}.json")
    with open(created_deal_filename, "w") as file:
        json.dump(created_deal_payload, file, indent=4)
    
    # Generate "UPDATED" deal
    updated_deal_payload = generate_deal_payload(current_id, "UPDATED")
    updated_deal_filename = os.path.join(folder_name, f"deal_updated_{current_id}.json")
    with open(updated_deal_filename, "w") as file:
        json.dump(updated_deal_payload, file, indent=4)
    
    # Increment deal ID
    current_id += 1

print(f"Generated {num_deals} 'CREATED' and 'UPDATED' deal payloads in '{folder_name}' folder.")
