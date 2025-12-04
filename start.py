"""
Helper script to load environment variables from .env file and start the agent
"""
import os
import sys

def load_env_file(filepath='.env'):
    """Load environment variables from .env file"""
    if not os.path.exists(filepath):
        print(f"⚠ Warning: {filepath} not found")
        print("Agent will run without API key (fallback mode)")
        return False
    
    print(f"Loading environment variables from {filepath}...")
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if line and not line.startswith('#'):
                # Split on first = only
                if '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
                    if key.strip() == 'GEMINI_API_KEY':
                        print(f"✓ Loaded GEMINI_API_KEY")
    
    return True

if __name__ == "__main__":
    print("="*70)
    print("Cross-Sell Suggestion Agent - Startup")
    print("="*70)
    
    # Load .env file
    load_env_file()
    
    # Check if API key is set
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        print(f"✓ Gemini AI enabled ({api_key[:10]}...)")
    else:
        print("⚠ Gemini AI disabled (no API key)")
        print("  Set GEMINI_API_KEY in .env file or environment variable")
    
    print("="*70)
    print()
    
    # Start the agent
    print("Starting CSSA agent...\n")
    os.system("python cssa_agent.py")
