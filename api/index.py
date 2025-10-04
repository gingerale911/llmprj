from dotenv import load_dotenv
import os

load_dotenv()  # load environment variables from .env file
print('GOOGLE_API_KEY:', os.getenv('GOOGLE_API_KEY'))

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import re
import requests
from bs4 import BeautifulSoup


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

def is_url(query: str) -> bool:
	return re.match(r'https?://', query) is not None

def scrape_web(url: str) -> str:
	try:
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
		}
		resp = requests.get(url, headers=headers, timeout=10)
		resp.raise_for_status()
		soup = BeautifulSoup(resp.text, 'html.parser')
		# Try to extract main text content
		paragraphs = [p.get_text() for p in soup.find_all('p')]
		text = '\n'.join(paragraphs)
		return text[:80000]  # send up to 8k chars to LLM
	except Exception as e:
		return None


@app.get("/")
async def hello():
	return {"hello": "world"}



@app.post("/")
async def answer_with_llm(request: QuestionRequest):
	text = request.question
	import json
	# Always ask LLM if scraping is needed and for the URL
	prompt = (
		"Given the user's question, if it requires web scraping (e.g., contains a URL or asks for live data), "
		"respond ONLY with a JSON object: {\"scrape\": true, \"url\": \"<url to scrape>\"}. "
		"If not, respond ONLY with a JSON object: {\"scrape\": false, \"answer\": \"<your answer>\"}. "
		"Do not include any other text. Question: " + text
	)
	try:
		resp = model.generate_content(prompt)
		try:
			llm_json = json.loads(resp.text)
		except Exception:
			return JSONResponse({"error": "LLM did not return valid JSON: " + resp.text}, status_code=500)
		if llm_json.get('scrape') and llm_json.get('url'):
			# Scrape the URL, then send content to LLM for answer
			scraped_text = scrape_web(llm_json['url'])
			if not scraped_text:
				return JSONResponse({"error": "Scraping failed or returned no content."}, status_code=500)
			llm_prompt = (
				f"Given the following web page content, answer the user's query or summarize as appropriate.\n\n"
				f"User Query: {text}\n\nWeb Page Content:\n{scraped_text}"
			)
			try:
				final_resp = model.generate_content(llm_prompt)
				return JSONResponse({"answer": final_resp.text})
			except Exception as e:
				return JSONResponse({"error": str(e)}, status_code=500)
		elif not llm_json.get('scrape'):
			return JSONResponse({"answer": llm_json.get('answer', resp.text)})
		else:
			return JSONResponse({"error": "LLM response missing required fields: " + resp.text}, status_code=500)
	except Exception as e:
		return JSONResponse({"error": str(e)}, status_code=500)
	

#curl -X POST https://web-production-dad2a.up.railway.app/ \
# -H "Content-Type: application/json" \
#  -d '{"question": "What is the capital of France?"}'