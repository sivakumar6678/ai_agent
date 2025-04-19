# ai_clients/gemini.py

import google.generativeai as genai
from config import GEMINI_API_KEY

# Setup
genai.configure(api_key=GEMINI_API_KEY)

# Choose the right model (gemini-1.5-pro or gemini-1.5-flash if you got access)
MODEL = "models/gemini-1.5-flash"

def get_gemini_response(prompt):
    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error while generating content: {str(e)}"
