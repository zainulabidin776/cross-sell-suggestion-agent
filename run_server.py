"""
Simple server startup script that ensures .env is loaded
Run this instead of python cssa_agent.py
"""
import os
from dotenv import load_dotenv

# Load .env file first
load_dotenv()

# Verify API key is loaded
api_key = os.getenv('GEMINI_API_KEY')
if api_key:
    print(f"✓ API Key loaded: {api_key[:15]}...")
else:
    print("✗ WARNING: GEMINI_API_KEY not found in environment!")
    print("  Make sure .env file exists with GEMINI_API_KEY=your_key")

# Now import and run the app
import cssa_agent

if __name__ == '__main__':
    print("\nStarting Cross-Sell Suggestion Agent...")
    print("Server will be available at http://127.0.0.1:5000")
    print("Press CTRL+C to stop\n")
    
    cssa_agent.app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False  # Important: prevents env variable loss
    )
