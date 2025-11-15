# Cross-Sell Suggestion Agent — Project Report (Draft)

Authors:
- Awaiz Ali Khan (22I-2509) — Project Manager
- Zain ul Abideen (22I-2738) — ML Developer
- Kamran Ali (22I-2589) — Backend Developer

## 1. Project Overview & Objectives

Problem: Increase average order value by suggesting complementary products (cross-sell) during customer interactions.

Objectives:
- Implement an AI-driven recommendation agent exposing HTTP APIs.
- Support Supervisor–Worker registry architecture and health checks.
- Provide short-term memory and persist interactions for analysis.
- **Use real product data from external APIs** (not hardcoded).

## 2. Project Management Artifacts (summary)

- WBS: Requirements → Design → Implementation → Testing → Documentation → Demo
- Schedule: 2 weeks implementation + 1 week testing & report
- Cost estimate: student project (time-based)
- Risk plan: data privacy, model bias, integration failures, API downtime

## 3. System Design & Architecture

Architecture: External API → Cached JSON → ProductDatabase (in-memory) → RecommendationEngine → User, with STM (in-memory) and LTM (SQLite). UI and Test harness communicate with the agent.

**Data Flow:**
```
Fake Store API (external, real products)
    ↓ [fetch once via setup.py]
products.json (cached locally)
    ↓ [load on startup]
ProductDatabase (in-memory)
    ↓
RecommendationEngine → suggestions
    ↓
User sessions → LTM (SQLite, persistent)
```

Components:
- `cssa_agent.py`: Flask app, RecommendationEngine, STM, LTM, API endpoints
- `data_loader.py`: Fetches products from Fake Store API
- `ui/`: Minimal demo web interface
- `tests/`: pytest unit tests + integration script

## 4. Memory Strategy

- **Short-term memory:** In-memory per-session buffer, max 100 interactions per session. Tracks recent user actions within a session.
- **Long-term memory:** SQLite persistence (`cssa_memory.db`) for session interactions and search history. Enables session history replay and analytics.

## 5. Data & Product Catalog

**Real Data Source:** Fake Store API (https://fakestoreapi.com/products) — 20 free products across multiple categories.

**Why Real API:**
- Demonstrates real-world API integration (not hardcoded).
- Shows production readiness (graceful fallback if API down).
- Graders can inspect actual product recommendations.

**Process:**
1. Run `python setup.py` once to fetch real products
2. Products cached in `products.json`
3. Agent loads JSON on startup (no DB setup needed)
4. Cross-sell suggestions auto-generated from product categories

## 6. Database Strategy

**Product Catalog:** JSON file (`products.json`) — simple, portable, real data.
- Why not PostgreSQL for this project: Overkill for demo, no server setup, good grading clarity.
- Future: PostgreSQL for multi-instance deployments and dynamic product updates.

**Interactions (LTM):** SQLite (`cssa_memory.db`) — lightweight, file-based, zero setup.
- Schema: `sessions` (session metadata) and `interactions` (timestamped events).
- Why SQLite: ACID compliant, portable, perfect for <1M records, single file backup.

## 7. API Contract (samples)

- `POST /api/recommend` {"product_id": "prod_1", "session_id": "s1", "limit": 3}
- `POST /api/search` {"query": "smartphone"}
- `GET /api/memory/{session_id}` → returns persisted interactions
- `GET /openapi.json` → OpenAPI spec for Swagger UI

## 8. Integration Plan

- Supervisor polls `/health` and `/api/status`.
- Supervisor discovers capabilities via `/api/registry`.
- All interactions persisted to LTM for audit/replay.

## 9. Progress & Lessons Learned

- Implemented working prototype with real API data, schema validation, dual-tier memory, UI, and comprehensive logging.
- Lesson: Balancing simplicity (JSON caching) with scalability (PostgreSQL-ready).

## 10. Next Steps

- Optional: Add PostgreSQL for production scaling.
- Optional: Add CI/CD pipeline (GitHub Actions).
- Demo: Show real product recommendations from Fake Store API.


