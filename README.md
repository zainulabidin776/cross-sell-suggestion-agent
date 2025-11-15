# Cross-Sell Suggestion Agent (CSSA)

Lightweight Flask agent that returns cross-sell product recommendations using real product data from external APIs.

## Quick Start (Windows cmd)

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Load Real Product Data (Recommended)

Before running the agent, fetch real products from Fake Store API:

```
python setup.py
```

This fetches 20 products from https://fakestoreapi.com/products and caches them locally in `products.json`. If the API is unavailable, the agent falls back to hardcoded demo data.

## Run the Agent

```
python cssa_agent.py
```

- Demo UI: http://127.0.0.1:5000/
- Swagger API Docs: http://127.0.0.1:5000/ui/swagger.html
- Health Check: http://127.0.0.1:5000/health

## Run Tests

```
python test_agent.py
pytest -q
```

## Architecture

- **Product Data:** Loaded from `products.json` (fetched from external API), with fallback to hardcoded data.
- **STM (Short-Term Memory):** In-memory per-session interaction buffer.
- **LTM (Long-Term Memory):** SQLite persistence for session interactions (`cssa_memory.db`).
- **Recommendations:** Based on product category matching and cross-sell relationships.

## Files

- `cssa_agent.py` - Main Flask app
- `data_loader.py` - Fetches products from Fake Store API
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

