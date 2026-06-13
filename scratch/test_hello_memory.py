import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from rag import run_rag_query

try:
    print("Running query 1...")
    res = run_rag_query("hello", user_id="U123", channel_id="C123")
    print(res)
    
    print("Running query 2...")
    res2 = run_rag_query("how are you?", user_id="U123", channel_id="C123")
    print(res2)
except Exception as e:
    print("Error:", repr(e))
