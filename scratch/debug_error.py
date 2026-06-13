import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from rag import build_rag_chain, SESSION_MEMORY
import traceback

user_id = "U123"
channel_id = "C123"

try:
    chain = build_rag_chain(top_k=4, user_id=user_id, channel_id=channel_id)
    result = chain.invoke({"question": "what is the scope in HRM", "chat_history": []})
    print("SUCCESS:", result.get("answer", ""))
except Exception as e:
    print("FULL TRACEBACK:")
    traceback.print_exc()
