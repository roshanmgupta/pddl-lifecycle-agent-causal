import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip().strip('"').strip("'")

from langchain_openai import ChatOpenAI
from pydantic import BaseModel

class DummyTest(BaseModel):
    status: str
    message: str

candidate_models = [
    "google/gemini-2.0-flash-lite-preview-02-05:free",
    "google/gemini-2.0-pro-exp-02-05:free",
    "deepseek/deepseek-r1:free",
    "deepseek/deepseek-r1-distill-llama-70b:free",
    "meta-llama/llama-3-8b-instruct:free",
    "qwen/qwen-2-7b-instruct:free",
    "mistralai/mistral-7b-instruct:free"
]

print("Testing OpenRouter free models...")
openrouter_key = os.getenv("OPENROUTER_API_KEY")

working_models = []
for model in candidate_models:
    try:
        print(f"Testing {model}...")
        llm = ChatOpenAI(
            model_name=model,
            openai_api_key=openrouter_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.0,
            max_retries=1
        )
        s_llm = llm.with_structured_output(DummyTest)
        res = s_llm.invoke("Respond with status='ok' and message='hello'")
        print(f"SUCCESS: {model} -> {res}")
        working_models.append(model)
    except Exception as e:
        print(f"FAILED {model}: {e}")

print("\nWorking models list:", working_models)
