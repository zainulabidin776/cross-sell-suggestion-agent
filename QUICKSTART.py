#!/usr/bin/env python
"""
Quick Start Guide for Cross-Sell Suggestion Agent

Run this script to see a walkthrough of the project.
"""

import os
import sys
import json

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def main():
    print_section("CSSA Project Quick Start")
    
    print("This project contains:")
    print("  • cssa_agent.py       - Main Flask HTTP API")
    print("  • data_loader.py      - Fetch real products from Fake Store API")
    print("  • ui/                 - Demo web interface")
    print("  • tests/              - Unit and integration tests")
    print("  • products.json       - Cached product data (auto-generated)")
    print("  • cssa_memory.db      - Session history database (auto-generated)")
    
    print_section("Setup (one-time)")
    print("1. Create virtual environment:")
    print("   python -m venv venv")
    print("\n2. Activate it:")
    print("   Windows: venv\\Scripts\\activate")
    print("   Mac/Linux: source venv/bin/activate")
    print("\n3. Install dependencies:")
    print("   pip install -r requirements.txt")
    print("\n4. Fetch real product data from Fake Store API:")
    print("   python setup.py")
    print("   ✓ This fetches 20 real products and saves to products.json")
    
    print_section("Run the Agent")
    print("python cssa_agent.py")
    print("\nThen visit:")
    print("  • Demo UI:           http://127.0.0.1:5000/")
    print("  • API Documentation: http://127.0.0.1:5000/ui/swagger.html")
    print("  • Health Check:      http://127.0.0.1:5000/health")
    
    print_section("Run Tests (keep agent running in another terminal)")
    print("# Integration tests (uses requests library)")
    print("python test_agent.py")
    print("\n# Unit tests (pytest)")
    print("pytest -q")
    
    print_section("Example API Calls")
    print("# Get recommendations for a product")
    print('curl -X POST http://127.0.0.1:5000/api/recommend \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"product_id": "prod_1", "limit": 3}\'')
    print("\n# Search for products")
    print('curl -X POST http://127.0.0.1:5000/api/search \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"query": "electronics"}\'')
    print("\n# Check session memory")
    print("curl http://127.0.0.1:5000/api/memory")
    
    print_section("Docker (Optional)")
    print("# Build and run in container")
    print("docker build -t cssa-agent .")
    print("docker run -p 5000:5000 cssa-agent")
    print("\n# Or with docker-compose:")
    print("docker-compose up --build")
    
    print_section("Data & Architecture")
    print("✓ Real data: Products fetched from https://fakestoreapi.com/")
    print("✓ Caching: Saved to products.json (portable, no DB setup)")
    print("✓ STM: In-memory session interactions")
    print("✓ LTM: SQLite persistence (cssa_memory.db)")
    print("\nSee ARCHITECTURE.md for detailed strategy")
    
    print_section("Project Files")
    files = {
        'cssa_agent.py': 'Main agent, Flask routes, API endpoints',
        'data_loader.py': 'Fetch products from external API',
        'setup.py': 'Setup script to initialize data',
        'test_agent.py': 'Integration test suite',
        'tests/test_rec_engine.py': 'Unit tests',
        'ui/index.html': 'Demo web interface',
        'ui/swagger.html': 'API documentation UI',
        'openapi.json': 'OpenAPI spec',
        'products.json': 'Cached product data',
        'cssa_memory.db': 'Session history database',
        'README.md': 'Overview and quick start',
        'ARCHITECTURE.md': 'Database and scaling strategy',
        'report.md': 'Project report (convert to PDF)',
        'slides.md': 'Presentation slides (convert to PPTX)',
    }
    
    for fname, desc in files.items():
        status = "✓" if os.path.exists(fname) or fname in ['products.json', 'cssa_memory.db'] else "○"
        print(f"  {status} {fname:30} - {desc}")
    
    print_section("Troubleshooting")
    print("Q: Import error 'jsonschema not found'?")
    print("   A: Ensure venv is activated and pip install -r requirements.txt ran")
    print("\nQ: API data won't load?")
    print("   A: Run 'python setup.py' to fetch from Fake Store API")
    print("   B: If API is down, agent will use fallback hardcoded data")
    print("\nQ: Swagger UI shows 'Fetch error'?")
    print("   A: Restart the agent (flask detects code changes but may need manual restart)")
    print("   B: Check that /openapi.json endpoint is working")
    print("\nQ: How do I see the products?")
    print("   A: python -c \"import json; print(json.dumps(json.load(open('products.json')), indent=2)[:500])\"")
    
    print_section("Next Steps for Presentation")
    print("1. Run setup.py to load real data")
    print("2. Start the agent and test via UI")
    print("3. Show Swagger documentation")
    print("4. Run integration tests to show reliability")
    print("5. Discuss architecture and data strategy")
    print("6. Optional: Show Docker deployment")
    
    print("\n✓ Ready to demo! Questions? See README.md or ARCHITECTURE.md\n")

if __name__ == "__main__":
    main()
