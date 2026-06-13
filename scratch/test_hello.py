import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from rag import run_rag_query

try:
    print("Running query...")
    res = run_rag_query("hello", user_id="U123", channel_id="C123")
    print(res)
except Exception as e:
    print("Error:", repr(e))
