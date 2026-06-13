import requests

url = "http://127.0.0.1:8000/api/query"
payload = {
    "question": "What is HRM",
    "conversation_history": [
        {"role": "assistant", "content": "Good afternoon. What knowledge can I retrieve for you today?"}
    ]
}

res = requests.post(url, json=payload)
print("Status Code:", res.status_code)
print("Response JSON:", res.json())
