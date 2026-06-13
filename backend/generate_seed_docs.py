import os
import random

DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "test_docs")

os.makedirs(DOCS_DIR, exist_ok=True)

CATEGORIES = [
    ("HR_Policy", "This document outlines the human resources policy for {topic}. The policy is effective immediately and applies to all full-time employees. Key points include: \n- Compliance with state and federal regulations.\n- Expected conduct regarding {topic}.\n- Disciplinary actions for non-compliance."),
    ("Engineering_Spec", "Technical Specification: {topic}\nVersion: 1.{v}\n\nOverview:\nThis system is designed to handle {topic} at scale. Architecture involves microservices written in Go and Node.js. Databases used include PostgreSQL for transactional data and Redis for caching.\n\nAPI Endpoints:\n- /api/v1/{topic}/status\n- /api/v1/{topic}/metrics"),
    ("Finance_Report", "Q{v} Financial Summary - {topic}\n\nRevenue for this quarter exceeded expectations in the {topic} sector by {num}%. Operating costs remained stable. Major investments were made in cloud infrastructure to support growth. We project a steady increase in {topic} demand for the upcoming fiscal year."),
    ("Product_Playbook", "Sales & Product Playbook: {topic}\n\nTarget Audience: Enterprise customers needing {topic} solutions.\nKey Value Proposition: Our platform reduces {topic} overhead by 40%.\nCompetitor Analysis: Competitors lack our seamless integration capabilities.\nObjection Handling: If they say it's too expensive, highlight the long-term ROI of {num}%."),
    ("Security_Guideline", "InfoSec Guideline: {topic}\n\nAll {topic} systems must comply with SOC2 standards. Data encryption at rest (AES-256) and in transit (TLS 1.3) is mandatory. Access to {topic} databases requires MFA and is granted on a least-privilege basis. Regular audits will be conducted every {num} months.")
]

TOPICS = [
    "Remote Work", "Data Privacy", "Cloud Migration", "Employee Onboarding",
    "API Rate Limiting", "Quarterly Forecasting", "Enterprise Sales",
    "Zero Trust Architecture", "Disaster Recovery", "Payment Processing",
    "Customer Success", "Inventory Management", "Machine Learning Infrastructure",
    "Frontend Frameworks", "Marketing Automation", "Performance Reviews"
]

def generate_docs(count=50):
    for i in range(1, count + 1):
        cat_name, template = random.choice(CATEGORIES)
        topic = random.choice(TOPICS)
        content = template.format(topic=topic, v=random.randint(1, 9), num=random.randint(10, 80))
        filename = f"{cat_name}_{topic.replace(' ', '_')}_{i}.txt"
        filepath = os.path.join(DOCS_DIR, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
            
    print(f"Generated {count} documents in {DOCS_DIR}")

if __name__ == "__main__":
    generate_docs(50)
