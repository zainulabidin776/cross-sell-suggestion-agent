import pytest
from cssa_agent import ProductDatabase, RecommendationEngine


def test_generate_recommendations_basic():
    pdb = ProductDatabase()
    rec = RecommendationEngine(pdb)
    results = rec.generate_recommendations('laptop', user_history=None, limit=3)
    assert isinstance(results, list)
    assert len(results) > 0
    # Check structure
    for r in results:
        assert 'product_id' in r
        assert 'confidence_score' in r
