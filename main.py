import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if api_key and api_key != "your_api_key_here":
    genai.configure(api_key=api_key)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class OptimizeRequest(BaseModel):
    code: str
    language: str

@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

@app.post("/optimize")
async def optimize_code(request: OptimizeRequest):
    code = request.code
    lang = request.language

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        return {
            "optimized_code": code,
            "explanation": "Please add your GEMINI_API_KEY to the .env file in the GREEN directory to enable AI optimization.",
            "estimated_cpu_savings": "-",
            "estimated_memory_savings": "-",
            "green_score": 0
        }

    try:
        # Dynamically find an available model
        model_name = "gemini-1.5-pro-latest" # safe fallback
        try:
            available_models = []
            for m in genai.list_models():
                if "generateContent" in m.supported_generation_methods:
                    available_models.append(m.name)
            if available_models:
                # prefer flash, then pro, then anything
                flash_models = [m for m in available_models if "flash" in m.lower()]
                pro_models = [m for m in available_models if "pro" in m.lower()]
                if flash_models:
                    model_name = flash_models[0]
                elif pro_models:
                    model_name = pro_models[0]
                else:
                    model_name = available_models[0]
        except Exception:
            pass
            
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
Act as an expert "Green Code" software engineer. Analyze this {lang} code for performance and memory optimization.
Identify nested loops, unnecessary list comprehensions, inefficient data structures, and opportunities for vectorization or generators.

Code:
```
{code}
```

Return your analysis STRICTLY as a JSON object with this exact structure (no markdown fences, just the JSON):
{{
    "optimized_code": "<your refactored code here>",
    "explanation": "<brief explanation of what you changed to improve efficiency>",
    "estimated_cpu_savings": "<percentage, e.g., '20%'>",
    "estimated_memory_savings": "<percentage, e.g., '40%'>",
    "green_score": <number out of 100 representing how efficient the NEW code is compared to the original>
}}
"""
        response = model.generate_content(prompt)
        text_resp = response.text.strip()
        
        # Extract everything between the first '{' and the last '}'
        start_idx = text_resp.find('{')
        end_idx = text_resp.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
            json_str = text_resp[start_idx:end_idx+1]
        else:
            json_str = text_resp
            
        return json.loads(json_str)

    except json.JSONDecodeError as e:
        raw = text_resp if 'text_resp' in locals() else str(e)
        return {
            "optimized_code": code,
            "explanation": f"JSON parse error. Raw response from Gemini was:\n\n{raw}",
            "estimated_cpu_savings": "0%",
            "estimated_memory_savings": "0%",
            "green_score": 0
        }
    except Exception as e:
        error_msg = f"Google Gemini API error: {str(e)}"
        try:
            models = [m.name for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
            if models:
                error_msg += f" | Available models for your key: {', '.join(models)}"
        except:
            pass
            
        return {
            "optimized_code": code,
            "explanation": error_msg,
            "estimated_cpu_savings": "0%",
            "estimated_memory_savings": "0%",
            "green_score": 0
        }
