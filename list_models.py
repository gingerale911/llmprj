# list_models.py
import os
import google.generativeai as genai

# ① Read and configure your API key
key = os.getenv("GOOGLE_API_KEY")
if not key:
    raise RuntimeError("Please set GOOGLE_API_KEY")
genai.configure(api_key=key)

# ② List & print each model—this will dump the full object repr
for m in genai.list_models():
    print(m)
