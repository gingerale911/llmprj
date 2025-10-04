from dotenv import load_dotenv
import os

load_dotenv()  # load environment variables from .env file
print('GOOGLE_API_KEY:', os.getenv('GOOGLE_API_KEY'))
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash-lite")


app = FastAPI()

# Add CORS middleware to allow requests from any origin
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


class QuestionRequest(BaseModel):
	question: str


@app.get("/")
async def hello():
	return {"hello": "world"}


@app.post("/")
async def answer_with_llm(request: QuestionRequest):
	text = request.question
	try:
		resp = model.generate_content(text)
		return JSONResponse([resp.text])
	except Exception as e:
		return JSONResponse({"error": str(e)}, status_code=500)
	

#curl -X POST https://web-production-dad2a.up.railway.app/ \
# -H "Content-Type: application/json" \
#  -d '{"question": "What is the capital of France?"}'