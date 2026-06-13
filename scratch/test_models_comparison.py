import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

for model in ["gemini-1.5-flash", "gemini-3.5-flash"]:
    print(f"Testing model: {model}")
    try:
        llm = ChatGoogleGenerativeAI(
            model=model,
            temperature=0,
            google_api_key=GOOGLE_API_KEY
        )
        res = llm.invoke("What is the capital of France?")
        print(f"  SUCCESS! Answer: {res.content}")
    except Exception as e:
        print(f"  FAILED: {e}")
