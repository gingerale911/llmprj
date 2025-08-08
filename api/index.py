from dotenv import load_dotenv
import os


load_dotenv()  # load environment variables from .env file
print('GOOGLE_API_KEY:', os.getenv('GOOGLE_API_KEY'))
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import google.generativeai as genai


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("models/gemini-1.5-flash-8b")

app = FastAPI()

class QuestionRequest(BaseModel):
    question: str

@app.get("/")
async def hello():
    return {"hello": "world"}

@app.post("/")
async def answer_with_llm(request: QuestionRequest):
    text = request.question
    resp = model.generate_content(text)
    return JSONResponse([resp.text])
