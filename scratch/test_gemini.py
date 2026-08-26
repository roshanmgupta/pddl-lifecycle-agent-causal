import os
import dotenv
dotenv.load_dotenv(override=True)
from langchain_google_genai import ChatGoogleGenerativeAI

key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
print("Key present:", bool(key))

models_to_test = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-pro",
    "gemini-1.5-pro-latest",
    "gemini-2.0-flash-exp"
]

for m in models_to_test:
    try:
        llm = ChatGoogleGenerativeAI(
            model=m,
            google_api_key=key,
            temperature=0.0
        )
        res = llm.invoke("Hi")
        print(f"Model '{m}' -> SUCCESS: {res.content}")
        break
    except Exception as e:
        print(f"Model '{m}' -> FAILED: {e}")
