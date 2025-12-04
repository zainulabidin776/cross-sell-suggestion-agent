# Cross-Sell Suggestion Agent - Quick Start

## What This Does
A simple AI-powered agent that generates cross-sell product recommendations using Google Gemini 1.5 Flash. When you type a product name (like "laptop" or "mouse"), it suggests 0-5 related products that are commonly bought together.

## How to Use

### 1. Make Sure Your API Key is Set
Edit the `.env` file and add your Gemini API key:
```
GEMINI_API_KEY=your_actual_api_key_here
```

### 2. Start the Server
```bash
python cssa_agent.py
```

### 3. Open the Web Interface
Open your browser to: **http://127.0.0.1:5000**

### 4. Get Recommendations
- Type a product name in "Product ID" field (e.g., `laptop`, `mouse`, `smartphone`)
- Set the limit (0-5 recommendations)
- Click "Get Recommendations"

## API Usage

### Request Format (JSON)
```json
{
  "product_id": "laptop",
  "limit": 3,
  "session_id": "optional_session_id"
}
```

### Response Format (JSON)
```json
{
  "status": "success",
  "product_id": "laptop",
  "limit": 3,
  "recommendations": [
    {
      "product_name": "Wireless Mouse",
      "reason": "Essential for laptop productivity and comfort",
      "category": "Computer Accessories",
      "estimated_price": "$29.99"
    },
    {
      "product_name": "Laptop Bag",
      "reason": "Protects your laptop during transport",
      "category": "Accessories",
      "estimated_price": "$45.99"
    }
  ],
  "model": "gemini-1.5-flash",
  "timestamp": "2025-12-05T03:34:21.898000"
}
```

## Features
✓ Uses Google Gemini 1.5 Flash AI model
✓ Accepts product names in natural language
✓ Returns 0-5 recommendations (configurable)
✓ JSON input and output
✓ Simple web interface included
✓ Real-time AI-generated suggestions

## Files
- `cssa_agent.py` - Main application
- `ui/index.html` - Web interface
- `ui/app.js` - Frontend JavaScript
- `ui/styles.css` - Styling
- `.env` - Configuration (API key)

## Test Examples
Try these products:
- laptop
- mouse  
- smartphone
- camera
- headphones
- tablet
- keyboard

## Troubleshooting

**"Quota exceeded" error:**
- Wait 60 seconds and try again
- Check your API usage at https://ai.dev/usage
- Make sure you're using a valid API key

**"Gemini AI not initialized":**
- Check that `.env` file exists
- Verify GEMINI_API_KEY is set correctly
- Restart the server after changing .env

**500 Internal Server Error:**
- Check the terminal for error messages
- Verify the server is running
- Wait if you hit rate limits
