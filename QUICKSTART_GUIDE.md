# Quick Start Guide - Cross-Sell Suggestion Agent

## Problem: "Gemini AI not initialized" Error

### Root Cause
The error occurs because the Flask reloader creates a child process that doesn't load the `.env` file properly.

### Solution: Use the `run_server.py` script

## Steps to Run Locally

### 1. Verify .env File Exists
```powershell
Get-Content .env
```

You should see:
```
GEMINI_API_KEY=AIzaSyCOnthZERijVc9xjphrTagRM3U0l2n9xmU
```

### 2. Stop All Python Processes
```powershell
Stop-Process -Name python -Force -ErrorAction SilentlyContinue
```

### 3. Start Server Using run_server.py
```powershell
python run_server.py
```

You should see:
```
✓ API Key loaded: AIzaSyCOnthZER...
Starting Cross-Sell Suggestion Agent...
Server will be available at http://127.0.0.1:5000
```

### 4. Test in Browser
Open: http://127.0.0.1:5000

Try these products:
- **laptop** - Will find in catalog and suggest related items
- **mouse** - Will use AI to generate creative recommendations
- **coffee maker** - AI will suggest complementary items
- **phone** - Will find smartphones in catalog

## How It Works

### Products in Catalog (70 products from APIs)
When you search for products like "laptop", "phone", "shirt":
1. System searches catalog by name
2. Uses **Gemini 2.0 Flash** to analyze the product
3. Suggests complementary items from the catalog

### Products NOT in Catalog  
When you search for "mouse", "guitar", "yoga mat":
1. System detects product not in catalog
2. Uses **Pure AI Generation** with Gemini 2.0 Flash
3. Creates creative, intelligent cross-sell suggestions
4. Returns AI-generated products with reasons

## API Response Format

### Success Response (Product in Catalog)
```json
{
  "status": "success",
  "product_id": "fakestore_1",
  "recommendations": [
    {
      "product_id": "fakestore_5",
      "name": "Wireless Mouse",
      "category": "electronics",
      "price": 29.99,
      "confidence_score": 0.89,
      "reason": "Perfect accessory for laptop users",
      "ai_powered": true,
      "model": "gemini-2.0-flash"
    }
  ],
  "model": "gemini-2.0-flash",
  "limit_enforced": 3
}
```

### Success Response (AI Generated)
```json
{
  "status": "success",
  "query_product": "mouse",
  "recommendation_type": "ai_generated",
  "recommendations": [
    {
      "product_id": "ai_generated_1",
      "name": "Ergonomic Mouse Pad",
      "category": "accessories",
      "price": "$15-$25",
      "confidence_score": 0.85,
      "reason": "Reduces wrist strain during extended use",
      "source": "ai_generated",
      "model": "gemini-2.0-flash"
    }
  ]
}
```

## Features

✅ Natural product search (use "laptop" instead of "fakestore_1")
✅ Works with ANY product name using AI
✅ Powered by Gemini 2.0 Flash (fastest, most efficient)
✅ No dummy data or fallbacks
✅ Maximum 5 recommendations per request
✅ Intelligent, contextual suggestions

## Troubleshooting

### Error: "Gemini AI not initialized"
**Solution:** Use `python run_server.py` instead of `python cssa_agent.py`

### Error: "Connection refused"
**Solution:** Make sure server is running in a separate terminal

### Error: "Product not found"
**This is not an error!** The system will use AI to generate recommendations for any product.

## Testing

Run comprehensive tests:
```powershell
python test_api.py
```

This tests:
1. Product in catalog (laptop)
2. Product NOT in catalog (mouse) - AI generation

## Deployment

When deploying to production:
1. Set `GEMINI_API_KEY` as environment variable
2. Use `gunicorn` instead of Flask dev server:
   ```bash
   gunicorn cssa_agent:app --bind 0.0.0.0:5000
   ```
3. Ensure `.env` file is **NOT** committed to Git (already in `.gitignore`)

## Project Summary

**Team:** Awaiz Ali Khan, Zain ul Abideen, Kamran Ali  
**Course:** SE4002 - Software Project Management  
**Model:** Google Gemini 2.0 Flash  
**Products:** 70 real products from Fake Store API + DummyJSON API  
**AI Mode:** Pure LLM recommendations, no rule-based fallbacks
