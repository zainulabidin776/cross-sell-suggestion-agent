"""
Google Gemini AI Integration for Enhanced Product Recommendations
"""

import os
import logging
import json
from typing import List, Dict, Optional

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("google-generativeai not installed. AI recommendations disabled.")

logger = logging.getLogger(__name__)


class GeminiRecommendationEngine:
    """Enhanced recommendation engine using Google Gemini AI"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini AI engine
        
        Args:
            api_key: Google Gemini API key. If None, will try to load from GEMINI_API_KEY env variable
        """
        self.enabled = False
        self.model = None
        
        if not GEMINI_AVAILABLE:
            logger.warning("Gemini AI not available - google-generativeai package not installed")
            return
        
        # Get API key from parameter or environment
        api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            logger.warning("Gemini API key not provided. Set GEMINI_API_KEY environment variable to enable AI recommendations")
            return
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.enabled = True
            logger.info("✓ Gemini AI initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI: {e}")
            self.enabled = False
    
    def generate_recommendations_from_catalog(self, 
                                              product: Dict, 
                                              all_products: Dict[str, Dict],
                                              limit: int = 5,
                                              user_history: Optional[List[Dict]] = None) -> List[Dict]:
        """
        Use Gemini AI to generate intelligent recommendations directly from the entire product catalog.
        No pre-computed cross-sell lists needed - pure LLM-based recommendations.
        
        Args:
            product: The main product dict the user is viewing
            all_products: Complete product catalog dictionary
            limit: Number of recommendations to return
            user_history: Optional user history to avoid repetitive suggestions
            
        Returns:
            List of AI-generated recommendations with reasons
        """
        if not self.enabled:
            logger.warning("Gemini AI not enabled, cannot generate LLM-based recommendations")
            return []
        
        try:
            # Filter out the current product and previously recommended items
            excluded_ids = {product.get('id')}
            if user_history:
                for item in user_history:
                    rec_id = item.get('data', {}).get('product_id')
                    if rec_id:
                        excluded_ids.add(rec_id)
            
            # Build catalog for LLM (limit to reasonable size to avoid token limits)
            catalog_items = []
            for pid, prod in all_products.items():
                if prod.get('id') not in excluded_ids and len(catalog_items) < 100:
                    catalog_items.append({
                        'product_id': pid,
                        'name': prod['name'],
                        'category': prod['category'],
                        'price': prod['price'],
                        'description': prod.get('description', '')[:100]
                    })
            
            if not catalog_items:
                logger.warning("No catalog items available for recommendations")
                return []
            
            # Build LLM prompt
            prompt = self._build_llm_catalog_prompt(product, catalog_items, limit)
            
            # Get AI recommendations
            logger.info(f"Querying Gemini AI for {limit} recommendations from {len(catalog_items)} products")
            response = self.model.generate_content(prompt)
            
            # Parse and enrich recommendations
            recommendations = self._parse_llm_catalog_response(response.text, all_products)
            
            logger.info(f"✓ Gemini AI generated {len(recommendations)} pure LLM recommendations")
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"LLM catalog recommendation failed: {e}")
            return []
    
    def _build_llm_catalog_prompt(self, product: Dict, catalog: List[Dict], limit: int) -> str:
        """Build a prompt for pure LLM-based recommendations from catalog"""
        
        prompt = f"""You are an expert e-commerce recommendation AI. A customer is currently viewing this product:

**CURRENT PRODUCT:**
- Name: {product['name']}
- Category: {product['category']}
- Price: ${product['price']}
- Description: {product.get('description', 'N/A')[:200]}

**YOUR TASK:**
Analyze the entire product catalog below and intelligently recommend the top {limit} products that would make excellent cross-sell suggestions. Consider:
1. Complementary functionality (items that work well together)
2. Category relationships (related but not identical categories)
3. Price range compatibility (avoid extreme price mismatches unless justified)
4. Customer value proposition (genuine utility to the customer)

**PRODUCT CATALOG:**
"""
        
        # Add catalog items (grouped by category for better context)
        from collections import defaultdict
        by_category = defaultdict(list)
        for item in catalog:
            by_category[item['category']].append(item)
        
        for category, items in sorted(by_category.items()):
            prompt += f"\n{category.upper()}:\n"
            for item in items[:20]:  # Limit per category
                prompt += f"  • {item['product_id']}: {item['name'][:60]} (${item['price']})\n"
        
        prompt += f"""

**OUTPUT FORMAT:**
Return ONLY a JSON array with exactly {limit} recommendations. Each item must have:
- product_id: the exact product_id from the catalog above
- reason: a compelling 10-15 word reason explaining WHY this complements the current product
- confidence_score: float between 0.5-0.95 indicating recommendation strength

Example format:
[
  {{
    "product_id": "dummyjson_15",
    "reason": "Essential accessory that protects your investment and extends product life",
    "confidence_score": 0.88
  }}
]

IMPORTANT: Return ONLY the JSON array, no markdown, no explanations, just pure JSON."""
        
        return prompt
    
    def _parse_llm_catalog_response(self, response_text: str, all_products: Dict) -> List[Dict]:
        """Parse LLM response and merge with full product data"""
        
        try:
            # Clean response
            response_text = response_text.strip()
            
            # Remove markdown code blocks
            if response_text.startswith('```'):
                lines = response_text.split('\n')
                response_text = '\n'.join(lines[1:-1] if lines[-1].strip() == '```' else lines[1:])
                if response_text.startswith('json'):
                    response_text = response_text[4:].strip()
            
            # Parse JSON
            ai_recommendations = json.loads(response_text)
            
            # Enrich with full product data
            enriched = []
            for ai_rec in ai_recommendations:
                pid = ai_rec.get('product_id')
                if pid and pid in all_products:
                    product = all_products[pid]
                    enriched.append({
                        'product_id': pid,
                        'name': product['name'],
                        'category': product['category'],
                        'price': product['price'],
                        'confidence_score': round(ai_rec.get('confidence_score', 0.75), 2),
                        'reason': ai_rec.get('reason', 'AI-recommended complementary product'),
                        'description': product.get('description', ''),
                        'image': product.get('image', ''),
                        'ai_powered': True
                    })
            
            return enriched
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {e}")
            logger.debug(f"Response text: {response_text[:500]}")
            return []
        except Exception as e:
            logger.error(f"Failed to enrich LLM recommendations: {e}")
            return []
            
            logger.info(f"✓ Gemini AI enhanced {len(recommendations)} recommendations")
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Gemini AI recommendation failed: {e}. Falling back to basic recommendations")
            return candidate_products[:limit]
    
    def _build_recommendation_prompt(self, product: Dict, candidates: List[Dict], limit: int) -> str:
        """Build a prompt for Gemini AI"""
        
        prompt = f"""You are an expert e-commerce recommendation system. A customer is viewing the following product:

Product: {product['name']}
Category: {product['category']}
Price: ${product['price']}
Description: {product.get('description', 'N/A')}

Based on this product, rank and select the top {limit} cross-sell recommendations from the following candidates. For each recommendation, provide:
1. The product ID
2. A brief, compelling reason why it complements the main product (max 15 words)
3. A confidence score (0-1)

Candidate Products:
"""
        
        for i, candidate in enumerate(candidates[:20], 1):  # Limit to first 20 to avoid token limits
            prompt += f"\n{i}. ID: {candidate.get('product_id', 'unknown')}, Name: {candidate['name'][:50]}, Category: {candidate['category']}, Price: ${candidate['price']}"
        
        prompt += f"""

Return your response as a JSON array with exactly {limit} items in this format:
[
  {{
    "product_id": "id_here",
    "reason": "Brief compelling reason here",
    "confidence_score": 0.85
  }}
]

Important: Return ONLY the JSON array, no additional text."""
        
        return prompt
    
    def _parse_ai_response(self, response_text: str, candidates: List[Dict]) -> List[Dict]:
        """Parse Gemini AI response and merge with product data"""
        
        try:
            # Clean response (remove markdown code blocks if present)
            response_text = response_text.strip()
            if response_text.startswith('```'):
                # Remove markdown code block markers
                lines = response_text.split('\n')
                response_text = '\n'.join(lines[1:-1] if lines[-1].strip() == '```' else lines[1:])
                if response_text.startswith('json'):
                    response_text = response_text[4:].strip()
            
            # Parse JSON
            ai_recommendations = json.loads(response_text)
            
            # Create product lookup
            product_lookup = {c.get('product_id'): c for c in candidates}
            
            # Merge AI insights with product data
            enhanced = []
            for ai_rec in ai_recommendations:
                product_id = ai_rec.get('product_id')
                if product_id in product_lookup:
                    product_data = product_lookup[product_id]
                    enhanced.append({
                        'product_id': product_id,
                        'name': product_data['name'],
                        'category': product_data['category'],
                        'price': product_data['price'],
                        'confidence_score': round(ai_rec.get('confidence_score', 0.7), 2),
                        'reason': ai_rec.get('reason', 'Recommended for you'),
                        'ai_powered': True
                    })
            
            return enhanced if enhanced else candidates
            
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            logger.debug(f"Response text: {response_text}")
            return candidates
    
    def generate_personalized_reason(self, main_product: Dict, recommended_product: Dict) -> str:
        """
        Generate a personalized recommendation reason using Gemini AI
        
        Args:
            main_product: The product the user is viewing
            recommended_product: The product being recommended
            
        Returns:
            A personalized recommendation reason
        """
        if not self.enabled:
            return f"Frequently bought with {main_product['name']}"
        
        try:
            prompt = f"""Generate a brief (max 12 words), compelling reason why someone buying "{main_product['name']}" ({main_product['category']}, ${main_product['price']}) would want to buy "{recommended_product['name']}" ({recommended_product['category']}, ${recommended_product['price']}).

Return only the reason text, no quotes or extra formatting."""
            
            response = self.model.generate_content(prompt)
            reason = response.text.strip().strip('"\'')
            
            return reason if len(reason) <= 100 else reason[:97] + "..."
            
        except Exception as e:
            logger.error(f"Failed to generate personalized reason: {e}")
            return f"Complements {main_product['name']}"


# Global instance (will be initialized in cssa_agent.py)
gemini_engine = None

def initialize_gemini(api_key: Optional[str] = None):
    """Initialize the global Gemini engine"""
    global gemini_engine
    gemini_engine = GeminiRecommendationEngine(api_key)
    return gemini_engine
