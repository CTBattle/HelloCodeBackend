from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os

# Load OpenAI key from Render environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Enable CORS (so your iOS app can connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request schema
class PromptRequest(BaseModel):
    prompt: str
    language: str
    useFString: bool = False

@app.post("/generate_code")
async def generate_code(req: PromptRequest):
    system_prompt = f"Generate {req.language} code for this: {req.prompt}"
    if req.language.lower() == "python" and req.useFString:
        system_prompt += " using Python f-strings."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": req.prompt}
            ]
        )
        code = response["choices"][0]["message"]["content"]
        return { "code": code }

    except Exception as e:
        return { "error": str(e) }
