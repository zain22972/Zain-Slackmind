import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=api_key)
try:
    print("Listing models with new google-genai SDK:")
    for m in client.models.list():
        print(f"- {m.name} (displayName: {m.display_name})")
except Exception as e:
    print("Error:", e)
