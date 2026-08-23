import urllib.request
import json

url = "https://openrouter.ai/api/v1/models"
req = urllib.request.Request(url)
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())
    
free_models = [m["id"] for m in data.get("data", []) if ":free" in m["id"] or m.get("pricing", {}).get("prompt") == "0"]
print("Currently available Free OpenRouter models:")
for m in free_models:
    print(" -", m)
