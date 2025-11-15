#!/usr/bin/env python
"""
Setup script to fetch real product data from Fake Store API.
Run this once before starting the agent:
    python setup.py
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from data_loader import load_and_cache

if __name__ == "__main__":
    print("=" * 60)
    print("CSSA Setup: Fetching real product data")
    print("=" * 60)
    
    products = load_and_cache()
    
    if products:
        print("\n✓ Setup complete!")
        print(f"  {len(products)} products loaded and cached")
        print("\nNow run the agent:")
        print("  python cssa_agent.py")
    else:
        print("\n✗ Setup failed - no products loaded")
        print("  The agent will use fallback hardcoded data")
        sys.exit(1)
