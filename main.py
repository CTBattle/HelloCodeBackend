from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os

app = FastAPI()

# Middleware to allow all origins during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load OpenAI API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Data model
class PromptRequest(BaseModel):
    prompt: str
    language: str
    useFString: bool = False

@app.post("/generate_code")
async def generate_code(req: PromptRequest):
    # ✅ Prevent sending blank input
    if not req.prompt.strip():
        return { "error": "Prompt cannot be empty." }

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
    except Exception as e:
        return {"error": str(e)}
