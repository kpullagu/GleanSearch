import os
import random
import json
from datetime import datetime, timedelta

output_dir = "sample_docs"
os.makedirs(output_dir, exist_ok=True)

# AAuthor configuration section
AUTHOR_ID = "KP"  # Your unique identifier
AUTHOR_NAME = "KPull"  # Your name
AUTHOR_TEAM = "AI"  # Your team


# Document structure definitions
marketing_content = {
    "reports": [
        {
            "title": "Q1 2024 Marketing Performance Report",
            "topics": [
                "Campaign ROI Analysis: Social Media vs Email",
                "Lead Generation Metrics",
                "Website Traffic Growth",
                "Conversion Rate Optimization Results",
                "Marketing Qualified Leads (MQL) Analysis"
            ]
        },
        {
            "title": "Digital Marketing Campaign Analysis",
            "topics": [
                "PPC Performance Metrics",
                "Social Media Engagement Rates",
                "Content Marketing Success Metrics",
                "Email Campaign Analytics",
                "Marketing Attribution Model Results"
            ]
        }
    ],
    "tags": ["Marketing", "Analytics", "Campaigns", "ROI", "Digital"]
}

engineering_content = {
    "handbooks": [
        {
            "title": "System Design Best Practices",
            "topics": [
                "Distributed Systems Architecture",
                "CAP Theorem Implementation",
                "Load Balancing Strategies",
                "Database Sharding Patterns",
                "Microservices Communication"
            ]
        },
        {
            "title": "Technical Architecture Guidelines",
            "topics": [
                "API Design Principles",
                "Scalability Patterns",
                "Fault Tolerance Strategies",
                "Performance Optimization",
                "Security Best Practices"
            ]
        }
    ],
    "tags": ["Engineering", "Architecture", "Technical", "Design", "Infrastructure"]
}

hr_content = {
    "policies": [
        {
            "title": "Employee Benefits and Leave Policy",
            "topics": [
                "Annual Leave Entitlement",
                "Sick Leave Policy",
                "Parental Leave Guidelines",
                "Work from Home Policy",
                "Professional Development Benefits"
            ]
        },
        {
            "title": "HR Guidelines and Procedures",
            "topics": [
                "Performance Review Process",
                "Career Development Framework",
                "Compensation Structure",
                "Employee Wellness Programs",
                "Remote Work Guidelines"
            ]
        }
    ],
    "tags": ["HR", "Policy", "Benefits", "Employee", "Guidelines"]
}

def generate_custom_properties(doc_type):
    # Add your identifier to all custom properties
    base_properties = {
        "author": AUTHOR_NAME,
        "team": AUTHOR_TEAM,
        "documentOwner": AUTHOR_ID,
        "lastModifiedBy": AUTHOR_ID
    }
    
    if doc_type == "marketing":
        return {
            **base_properties,  # Include base properties
            "department": "Marketing",
            "quarter": f"Q{random.randint(1,4)} 2024",
            "campaign_type": random.choice(["Digital", "Social", "Email", "Content"]),
            "business_unit": random.choice(["B2B", "B2C", "Enterprise"])
        }
    elif doc_type == "engineering":
        return {
            **base_properties,
            "department": "Engineering",
            "tech_stack": random.choice(["Cloud", "Backend", "Frontend", "Infrastructure"]),
            "complexity_level": random.choice(["Basic", "Intermediate", "Advanced"]),
            "last_reviewed": (datetime.now() - timedelta(days=random.randint(0,90))).strftime("%Y-%m-%d")
        }
    else:  # HR
        return {
            **base_properties,
            "department": "Human Resources",
            "policy_type": random.choice(["Leave", "Benefits", "Wellness", "Career"]),
            "applies_to": random.choice(["All Employees", "Full-Time", "Management"]),
            "effective_date": (datetime.now() - timedelta(days=random.randint(0,180))).strftime("%Y-%m-%d")
        }

def generate_document_content(doc_type, index):
    if doc_type == "marketing":
        content = marketing_content
        obj_type = "marketingDoc"
    elif doc_type == "engineering":
        content = engineering_content
        obj_type = "engineeringDoc"
    else:
        content = hr_content
        obj_type = "hrDoc"

    handbook = random.choice(content["reports" if doc_type == "marketing" else "handbooks" if doc_type == "engineering" else "policies"])
    title = f"{handbook['title']} - {index}"
    topics = random.sample(handbook['topics'], k=random.randint(2, len(handbook['topics'])))
    tags = random.sample(content['tags'], k=random.randint(2, 4))
    custom_props = generate_custom_properties(doc_type)
    
    content = f"""Title: {title}
ObjectType: {obj_type}
Tags: {', '.join(tags)}, {AUTHOR_ID}-docs
CustomProperties: {json.dumps(custom_props, indent=2)}

Body:
{title}

Document Information:
- Author: {AUTHOR_NAME}
- Team: {AUTHOR_TEAM}
- Document ID: {AUTHOR_ID}-{index}
- department: {custom_props['department']}

Executive Summary:
This document is part of the {AUTHOR_ID} document collection and provides detailed information about {handbook['title'].lower()}.

Key Topics Covered:
{chr(10).join('- ' + topic for topic in topics)}

Detailed Content:
"""
    # Rest of the content generation remains the same
    return content

# Generate 100 documents
doc_types = ["marketing"] * 33 + ["engineering"] * 34 + ["hr"] * 33  # Equal distribution
random.shuffle(doc_types)

start_num = random.randint(300, 10000)
for i in range(start_num, start_num + 100):
    doc_type = doc_types[(i - start_num) % len(doc_types)]
    content = generate_document_content(doc_type, i)
    
    filename = f"sample_doc_{i:03}.txt"
    with open(os.path.join(output_dir, filename), "w") as f:
        f.write(content)

print(f"Generated 100 documents in {output_dir}, starting from {start_num}")
