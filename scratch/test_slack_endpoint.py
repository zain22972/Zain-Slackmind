import requests

url = "http://127.0.0.1:8000/slack/events"
payload = {
    "token": "verification_token",
    "challenge": "challenge_string",
    "type": "event_callback",
    "event": {
        "type": "app_mention",
        "user": "U123456",
        "text": "<@U0123> hello",
        "ts": "12345.6789",
        "channel": "C123456"
    }
}
res = requests.post(url, json=payload)
print(res.status_code, res.text)
