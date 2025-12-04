# Getting Your Google Gemini API Key

## Step 1: Visit Google AI Studio
Go to [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)

## Step 2: Sign in with Google Account
Sign in with your Google account.

## Step 3: Create API Key
1. Click "Create API Key" button
2. Select an existing Google Cloud project or create a new one
3. Your API key will be generated

## Step 4: Copy the API Key
Copy the generated API key (it will look like: `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXX`)

## Step 5: Set the Environment Variable

### On Windows (PowerShell):
```powershell
$env:GEMINI_API_KEY="your_actual_api_key_here"
```

### On Windows (CMD):
```cmd
set GEMINI_API_KEY=your_actual_api_key_here
```

### On Linux/Mac:
```bash
export GEMINI_API_KEY="your_actual_api_key_here"
```

### Or create a .env file:
```bash
# Copy the example file
cp .env.example .env

# Edit .env and replace with your actual key
# GEMINI_API_KEY=your_actual_api_key_here
```

## Step 6: Verify Installation
```bash
python -c "import os; print('API Key Set!' if os.getenv('GEMINI_API_KEY') else 'API Key NOT Set')"
```

## Important Notes:
- Keep your API key secret and never commit it to version control
- The Gemini API has a free tier with generous limits
- The agent works without the API key but with basic recommendations only
- With AI enabled, you get intelligent, context-aware product suggestions

## Pricing (as of Dec 2024):
- **Free tier**: 60 requests per minute
- More than enough for development and small production deployments
- Check current pricing: [https://ai.google.dev/pricing](https://ai.google.dev/pricing)
