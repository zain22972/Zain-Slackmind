import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=api_key)

print("Listing and testing all models...")
try:
    models = list(client.models.list())
    print(f"Found {len(models)} models.")
    
    for m in models:
        # Skip embedding and other non-generation models
        if "embed" in m.name or "imagen" in m.name or "veo" in m.name or "lyria" in m.name or "clip" in m.name or "aqa" in m.name:
            continue
            
        print(f"Testing model: {m.name}...")
        try:
            response = client.models.generate_content(
                model=m.name,
                contents="What is 1+1?",
            )
            print(f"  SUCCESS! Response: {response.text.strip()}")
        except Exception as e:
            err_str = str(e)
            if "RESOURCE_EXHAUSTED" in err_str:
                print("  FAILED: RESOURCE_EXHAUSTED (Rate limit / Quota limit 0)")
            elif "PERMISSION_DENIED" in err_str:
                print("  FAILED: PERMISSION_DENIED (403 Access Denied)")
            else:
                print(f"  FAILED: {err_str}")
except Exception as e:
    print("Error listing/testing models:", e)
