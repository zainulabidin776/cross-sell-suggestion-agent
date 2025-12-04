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
            # Use Gemini 2.0 Flash for faster, more efficient responses
            self.model = genai.GenerativeModel(
                'gemini-2.0-flash-exp',
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.95,
                    'top_k': 40,
                    'max_output_tokens': 2048,
                }
            )
            self.enabled = True
            logger.info("[OK] Gemini 2.0 Flash initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI: {e}")
            self.enabled = False
    
    def generate_recommendations_from_catalog(self, 
                                              product: Dict, 
                                              all_products: Dict[str, Dict],
                                              limit: int = 5,
                                              user_id: Optional[str] = None) -> List[Dict]:
        """
        Pure Gemini 2.0 Flash recommendations - NO fallback, NO dummy data.
        
        Args:
            product: The main product dict the user is viewing
            all_products: Complete product catalog dictionary
            limit: Number of recommendations (max 5)
            user_id: Optional user identifier for personalization
            
        Returns:
            List of AI-generated recommendations with reasons
        """
        if not self.enabled:
            raise Exception("Gemini AI not initialized. Set GEMINI_API_KEY environment variable.")
        
        # Enforce max limit of 5
        limit = min(limit, 5)
        
        try:
            # Get current product ID to exclude
            current_product_id = None
            for pid, prod in all_products.items():
                if prod.get('id') == product.get('id'):
                    current_product_id = pid
                    break
            
            # Build catalog excluding current product
            catalog_items = []
            for pid, prod in all_products.items():
                if pid != current_product_id and len(catalog_items) < 70:
                    catalog_items.append({
                        'product_id': pid,
                        'name': prod['name'],
                        'category': prod['category'],
                        'price': prod['price'],
                        'description': prod.get('description', '')[:120]
                    })
            
            if not catalog_items:
                raise Exception("No products available in catalog for recommendations")
            
            # Build optimized prompt for Gemini 2.0 Flash
            prompt = self._build_gemini_prompt(product, catalog_items, limit, user_id)
            
            # Query Gemini 2.0 Flash
            logger.info(f"Querying Gemini 2.0 Flash for {limit} recommendations (user: {user_id or 'anonymous'})")
            response = self.model.generate_content(prompt)
            
            # Parse and validate JSON response
            recommendations = self._parse_gemini_response(response.text, all_products)
            
            if not recommendations:
                raise Exception("Gemini returned no valid recommendations")
            
            logger.info(f"[OK] Gemini generated {len(recommendations)} recommendations")
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Gemini recommendation failed: {e}")
            raise
    
    def _build_gemini_prompt(self, product: Dict, catalog: List[Dict], limit: int, user_id: Optional[str]) -> str:
        """Build optimized prompt for Gemini 2.0 Flash"""
        
        # Group products by category for better context
        from collections import defaultdict
        by_category = defaultdict(list)
        for item in catalog:
            by_category[item['category']].append(item)
        
        catalog_text = ""
        for category in sorted(by_category.keys()):
            items = by_category[category][:15]  # Limit per category
            catalog_text += f"\n{category.upper()}:\n"
            for item in items:
                catalog_text += f"  • {item['product_id']}: {item['name'][:55]} - ${item['price']}\n"
        
        user_context = f" for user {user_id}" if user_id else ""
        
        prompt = f"""You are an expert e-commerce AI recommending complementary products{user_context}.

CURRENT PRODUCT:
Name: {product['name']}
Category: {product['category']}
Price: ${product['price']}
Description: {product.get('description', 'N/A')[:180]}

PRODUCT CATALOG:{catalog_text}

TASK: Recommend exactly {limit} products from the catalog that:
1. Complement or enhance the current product
2. Make logical sense together (e.g., accessories, related items, upgrades)
3. Are relevant to the product category
4. Provide real value to the customer

RULES:
- Use ONLY product_id values from the catalog above
- Provide compelling, specific reasons (10-15 words)
- Confidence score: 0.70-0.95 (higher = stronger recommendation)
- Prioritize different categories when logical

OUTPUT FORMAT (JSON only, no markdown):
[
  {{
    "product_id": "exact_id_from_catalog",
    "reason": "Specific compelling reason why this complements the main product",
    "confidence_score": 0.85
  }}
]

Return ONLY valid JSON array with {limit} items. No markdown, no explanations."""
        
        return prompt
    
    def _parse_gemini_response(self, response_text: str, all_products: Dict) -> List[Dict]:
        """Parse and validate Gemini JSON response"""
        
        try:
            # Clean response text
            response_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                lines = response_text.split('\n')
                # Find actual JSON content
                for i, line in enumerate(lines):
                    if line.strip().startswith('['):
                        response_text = '\n'.join(lines[i:])
                        break
                # Remove trailing ```
                if response_text.endswith('```'):
                    response_text = response_text[:-3].strip()
            
            # Parse JSON
            ai_recommendations = json.loads(response_text)
            
            if not isinstance(ai_recommendations, list):
                raise ValueError("Response is not a JSON array")
            
            # Validate and enrich with full product data
            enriched = []
            for ai_rec in ai_recommendations:
                if not isinstance(ai_rec, dict):
                    continue
                    
                pid = ai_rec.get('product_id')
                if not pid or pid not in all_products:
                    logger.warning(f"Invalid product_id: {pid}")
                    continue
                
                product = all_products[pid]
                confidence = ai_rec.get('confidence_score', 0.75)
                
                # Validate confidence score
                if not isinstance(confidence, (int, float)) or confidence < 0.5 or confidence > 1.0:
                    confidence = 0.75
                
                enriched.append({
                    'product_id': pid,
                    'name': product['name'],
                    'category': product['category'],
                    'price': product['price'],
                    'confidence_score': round(confidence, 2),
                    'reason': ai_rec.get('reason', 'Recommended by AI')[:100],
                    'description': product.get('description', ''),
                    'image': product.get('image', ''),
                    'ai_powered': True,
                    'model': 'gemini-2.0-flash'
                })
            
            return enriched
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            logger.error(f"Response text: {response_text[:300]}")
            raise Exception(f"Invalid JSON from Gemini: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to process Gemini response: {e}")
            raise
            
            logger.info(f"[OK] Gemini AI enhanced {len(recommendations)} recommendations")
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
    
    def generate_generic_recommendations(self, product_name: str, limit: int = 5, user_id: Optional[str] = None) -> List[Dict]:
        """
        Generate recommendations for ANY product, even if not in catalog.
        Uses pure Gemini AI to suggest complementary items.
        
        Args:
            product_name: Natural product name (e.g., "mouse", "laptop", "shirt")
            limit: Number of recommendations (max 5)
            user_id: Optional user identifier
            
        Returns:
            List of AI-generated generic recommendations
        """
        if not self.enabled:
            raise Exception("Gemini AI not initialized")
        
        limit = min(limit, 5)
        
        try:
            prompt = f"""You are a cross-sell recommendation expert. A customer is interested in buying: "{product_name}"

Generate {limit} complementary product suggestions that work well with this item.

For each recommendation, provide:
1. Product name (creative but realistic)
2. Brief reason why it pairs well
3. Confidence score (0.7-0.95)
4. Estimated price range

Return ONLY a JSON array in this exact format:
[
  {{"name": "Product Name", "reason": "Why it complements the main product", "confidence": 0.85, "price": "$XX-$XX", "category": "category name"}}
]

Be creative, practical, and focus on genuine cross-sell value."""

            logger.info(f"Generating generic recommendations for: {product_name}")
            response = self.model.generate_content(prompt)
            
            # Parse response
            text = response.text.strip()
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            
            recommendations = json.loads(text)
            
            # Format to match standard structure
            formatted = []
            for idx, rec in enumerate(recommendations[:limit]):
                formatted.append({
                    'product_id': f'ai_generated_{idx+1}',
                    'name': rec.get('name', 'Product'),
                    'category': rec.get('category', 'General'),
                    'price': rec.get('price', 'N/A'),
                    'confidence_score': rec.get('confidence', 0.75),
                    'reason': rec.get('reason', f'Complements {product_name}'),
                    'ai_powered': True,
                    'model': 'gemini-2.0-flash',
                    'source': 'ai_generated'
                })
            
            logger.info(f"[OK] Generated {len(formatted)} AI recommendations for '{product_name}'")
            return formatted
            
        except Exception as e:
            logger.error(f"Generic recommendation failed: {e}")
            raise


# Global instance (will be initialized in cssa_agent.py)
gemini_engine = None

def initialize_gemini(api_key: Optional[str] = None):
    """Initialize the global Gemini engine"""
    global gemini_engine
    gemini_engine = GeminiRecommendationEngine(api_key)
    return gemini_engine
