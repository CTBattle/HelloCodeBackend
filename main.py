import time
from openai import OpenAI, RateLimitError
from fastapi import FastAPI
from pydantic import BaseModel
import os
from fastapi.middleware.cors import CORSMiddleware

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class PromptRequest(BaseModel):
    prompt: str
    language: str
    useFString: bool = False

app = FastAPI()

# CORS (allow requests from any frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fallback cooldown limiter
last_request_time = 0
cooldown_seconds = 2

@app.post("/generate_code")
async def generate_code(req: PromptRequest):
    global last_request_time
    now = time.time()
    if now - last_request_time < cooldown_seconds:
        return {"error": "You're sending requests too quickly. Please wait a moment."}
    last_request_time = now

    system_prompt = f"Generate {req.language} code for this: {req.prompt}"
    if req.language.lower() == "python" and req.useFString:
        system_prompt += " using Python f-strings"

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": req.prompt}
            ]
        )
        code = response.choices[0].message.content
        return {"code": code}

    except RateLimitError:
        return {"code": "# ⚠️ OpenAI rate limit hit.\n# Here's a sample fallback.\nprint('Hello from HelloCode!')"}

    except Exception as e:
        return {"error": f"⚠️ Server error: {str(e)}"}
