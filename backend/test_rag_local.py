from rag import run_rag_query

try:
    print("Running query...")
    res = run_rag_query("What is the scope of SRM?", user_id="U123", channel_id="C123")
    print(res)
except Exception as e:
    print("Error:", e)
