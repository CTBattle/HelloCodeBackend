import os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import OpenAI

# Load API key from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

# Allow frontend to access this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body structure
class PromptRequest(BaseModel):
    prompt: str
    language: str
    useFString: bool = False

@app.post("/generate_code")
async def generate_code(req: PromptRequest):
    try:
        system_prompt = f"Generate {req.language} code for: {req.prompt}"
        if req.language.lower() == "python" and req.useFString:
            system_prompt += " using f-strings"

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
