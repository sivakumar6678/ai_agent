# GEMINI_API_KEY = "AIzaSyABCM5aLFnDvdKbqte36XwW6N_e6kfALJo"
# config.py
"""
Configuration settings for the AI Code Agent.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# --- Gemini API Configuration ---
# IMPORTANT: Store your API key securely, preferably in an environment variable
# or a secret management system. Don't hardcode it here in production.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE") # Replace with your key or load from env
GEMINI_MODEL_NAME = "gemini-1.5-flash" # Or choose another suitable model

# --- Generation Parameters ---
TEMPERATURE = 0.7 # Controls randomness (0.0 = deterministic, 1.0 = max creativity)
MAX_OUTPUT_TOKENS = 2048 # Max length of the generated code

# --- Supported Languages ---
# Dictionary mapping language names (lowercase) to their details
SUPPORTED_LANGUAGES = {
    "python": {
        "extension": ".py",
        "filename": "generated_script.py",
        # Use a list for commands if compilation + execution is needed
        "execute_command": ["python", "{filename}"],
        "keywords": ["python", "py"]
    },
    "javascript": {
        "extension": ".js",
        "filename": "generated_script.js",
        "execute_command": ["node", "{filename}"],
        "keywords": ["javascript", "js", "node.js", "node"]
    },
    "c++": {
        "extension": ".cpp",
        "filename": "generated_script.cpp",
        "output_executable": "generated_executable", # Name for the compiled output
        # Separate compile and run steps
        "compile_command": ["g++", "{filename}", "-o", "{output_executable}", "-std=c++11"], # Added -std=c++11 for better compatibility
        "execute_command": ["./{output_executable}"],
        "keywords": ["c++", "cpp", "cplusplus"]
    },
    "java": {
        "extension": ".java",
        # Java filenames MUST match the public class name.
        # We'll assume the AI generates a class named 'Main'.
        # If not, this needs more complex parsing or prompting the AI.
        "filename": "Main.java",
        "class_name": "Main", # The expected main class name
        "compile_command": ["javac", "{filename}"],
        "execute_command": ["java", "{class_name}"],
        "keywords": ["java"]
    }
    # Add more languages here following the same structure
}

# --- File Handling ---
CODE_DIR = "generated_code" # Directory to save generated code

# --- Emojis for Logging ---
EMOJI_SUCCESS = "✅"
EMOJI_ERROR = "💥"
EMOJI_RETRY = "🔁"
EMOJI_GENERATE = "✨"
EMOJI_RUN = "🚀"
EMOJI_INFO = "ℹ️"
EMOJI_QUESTION = "❓"
EMOJI_CODE = "📄"
EMOJI_STOP = "🛑"