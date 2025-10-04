from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()  # This loads variables from .env into the environment

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

models = genai.list_models()
for model in models:
    print(model)