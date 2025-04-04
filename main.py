import openai
import os
from fastapi import FastAPI, Request
from pydantic import BaseModel

openai.api_key = os.getenv("OPENAI_API_KEY")

class PromptRequest(BaseModel):
    prompt: str
    language: str
    useFString: bool = False

app = FastAPI()

@app.post("/generate_code")
async def generate_code(req: PromptRequest):
    system_prompt = f"Generate {req.language} code for this: {req.prompt}"
    if req.language.lower() == "python" and req.useFString:
        system_prompt += " using Python f-strings"

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





from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Open for now
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate_code")
async def generate_code(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    language = data.get("language", "")
    use_fstring = data.get("useFString", False)

    # basic mock
    code = f"# Code for {language}: {prompt}\n"
    if language == "Python":
        code += f'print(f"{prompt}")' if use_fstring else f'print("{prompt}")'
    elif language == "HTML":
        code += f"<h1>{prompt}</h1>"
    else:
        code += f"// {prompt} in {language}"

    return {"code": code}
