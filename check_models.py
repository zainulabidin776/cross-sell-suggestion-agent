"""Check available Gemini models"""
from dotenv import load_dotenv
load_dotenv()

import os
import google.generativeai as genai

api_key = os.getenv('GEMINI_API_KEY')
print(f"API Key: {api_key[:15]}...")

genai.configure(api_key=api_key)

print("\nAvailable models:")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"  - {model.name}")
        print(f"    Display Name: {model.display_name}")
        print(f"    Methods: {model.supported_generation_methods}")
        print()
