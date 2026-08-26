import os
import sys
import dotenv
dotenv.load_dotenv()
from langchain_openai import ChatOpenAI

key = os.getenv("Groq_API_KEY") or os.getenv("GROQ_API_KEY")

models_to_test = [
    "gemma2-9b-it",
    "llama-3.2-11b-vision-preview",
    "llama-3.2-3b-preview",
    "llama-3.2-1b-preview",
    "llama-3.3-70b-instruct",
    "llama-3.1-70b-specdec",
    "compound-1",
    "groq-llama-3"
]

for m in models_to_test:
    try:
        llm = ChatOpenAI(
            model_name=m,
            openai_api_key=key,
            openai_api_base="https://api.groq.com/openai/v1",
            temperature=0.0,
            max_retries=0
        )
        resp = llm.invoke("Hello, reply with 'OK'")
        print(f"Model '{m}' -> SUCCESS: {resp.content}")
        break
    except Exception as e:
        print(f"Model '{m}' -> FAILED: {e}")
