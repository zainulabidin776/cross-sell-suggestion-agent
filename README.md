# Cross-Sell Suggestion Agent (CSSA)

**Intelligent Flask agent with LLM-powered product recommendations using Google Gemini AI**

## Features

- ✨ **Pure LLM Recommendations**: Uses Google Gemini AI to generate intelligent, context-aware cross-sell suggestions
- 📦 **70+ Real Products**: Fetches from Fake Store API (20) + DummyJSON API (50)
- 🎯 **Smart Fallback**: Works with rule-based recommendations if API key not set
- 🔄 **Dual-tier Memory**: STM (in-memory) + LTM (SQLite persistence)
- 🚀 **Production Ready**: Docker support, Gunicorn WSGI, comprehensive testing

## Quick Start

### 1. Install Dependencies

```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Get Google Gemini API Key (Recommended)

**To enable LLM-powered recommendations:**

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in and create an API key (free tier available)
3. Set the environment variable:

```powershell
# Windows PowerShell
$env:GEMINI_API_KEY="your_api_key_here"
```

```bash
# Linux/Mac
export GEMINI_API_KEY="your_api_key_here"
```

**Note**: Agent works without API key but uses basic rule-based recommendations.

### 3. Load Product Data

```bash
python setup.py
```

This fetches 70 products from multiple APIs and caches them in `products.json`.

### 4. Run the Agent

```bash
python cssa_agent.py
```

**Access the application:**
- 🌐 Demo UI: http://127.0.0.1:5000/
- 📖 API Docs: http://127.0.0.1:5000/ui/swagger.html
- ❤️ Health Check: http://127.0.0.1:5000/health

## How It Works

### LLM Mode (Gemini API Key Set)
1. User views a product
2. Agent sends product + entire catalog to Gemini AI
3. LLM analyzes and returns intelligent recommendations with reasons
4. No pre-computed cross-sell lists needed - pure AI intelligence

### Fallback Mode (No API Key)
1. Uses category-based matching
2. Pre-computed cross-sell relationships
3. Rule-based confidence scoring
4. Still functional, just less intelligent

## Testing

### Test Backend Integration
```bash
python test_backend_integration.py
```

### Test Limit Functionality
```bash
python test_limit_fix.py
```

### Full Test Suite
```bash
python test_agent.py
pytest -q
```

## API Usage

### Get Recommendations
```bash
curl -X POST http://127.0.0.1:5000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"product_id": "fakestore_1", "limit": 5}'
```

**Response:**
```json
{
  "recommendations": [
    {
      "product_id": "dummyjson_23",
      "name": "Product Name",
      "category": "electronics",
      "price": 49.99,
      "confidence_score": 0.87,
      "reason": "Perfect complement for enhanced functionality",
      "ai_powered": true
    }
  ]
}
```

### Search Products
```bash
curl -X POST http://127.0.0.1:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "laptop"}'
```

## Architecture

- **Product Data**: 70 products from Fake Store API + DummyJSON API cached in `products.json`
- **LLM Engine**: Google Gemini AI for intelligent recommendations (`gemini_ai.py`)
- **Fallback Engine**: Rule-based recommendations when LLM unavailable
- **STM**: In-memory per-session interaction buffer (max 100 items)
- **LTM**: SQLite persistence (`cssa_memory.db`) for session history
- **Frontend**: Unchanged - works seamlessly with both LLM and fallback modes

## Files

- `cssa_agent.py` - Main Flask app with LLM integration
- `gemini_ai.py` - Google Gemini AI recommendation engine
- `data_loader.py` - Fetches products from multiple APIs
- `setup.py` - Setup script to load product data
- `test_backend_integration.py` - Comprehensive backend test
- `ui/` - Demo web interface (unchanged)
- `tests/` - Unit and integration tests
- `products.json` - Cached product data (70 products)
- `cssa_memory.db` - Session history (auto-generated)

## Environment Variables

```bash
GEMINI_API_KEY=your_api_key_here  # Required for LLM mode
DEBUG=True                         # Flask debug mode
PORT=5000                          # Server port
```

See `.env.example` for more details.

## Docker (Optional)
- `setup.py` - Setup script to load data
- `ui/` - Demo web interface
- `tests/` - Unit and integration tests
- `products.json` - Cached product data (auto-generated)
- `cssa_memory.db` - Session history (auto-generated)

## Docker (Optional)

```
docker build -t cssa-agent:latest .
docker run -p 5000:5000 cssa-agent:latest
```

Or with compose:

```
docker-compose up --build
```

## Notes

- For production, set `DEBUG=False` and use a WSGI server (Gunicorn included in Dockerfile).
- PostgreSQL support for product catalog caching is optional; SQLite is used by default.

