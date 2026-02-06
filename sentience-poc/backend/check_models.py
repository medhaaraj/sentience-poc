import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("No API Key found")
    exit(1)

genai.configure(api_key=api_key)

print("Attempting to list models...")
try:
    with open("models.log", "w") as f:
        found = False
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                f.write(f"- {m.name}\n")
                found = True
        if not found:
            f.write("No models found with generateContent support.\n")
except Exception as e:
    with open("models.log", "w") as f:
        f.write(f"Error listing models: {e}\n")
