"""
Cross-Sell Suggestion Agent (CSSA)
Simplified Gemini 2.5 Flash Integration
"""

# Load environment variables FIRST
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, send_from_directory
import os
from datetime import datetime
import json
import logging
from typing import Dict, List, Optional

# Import Gemini AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cssa_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ============================================================================
# GEMINI 2.5 FLASH INITIALIZATION
# ============================================================================
gemini_model = None

def initialize_gemini():
    """Initialize Gemini 2.5 Flash model"""
    global gemini_model
    
    if not GEMINI_AVAILABLE:
        logger.error("google-generativeai not installed. Run: pip install google-generativeai")
        return False
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logger.error("GEMINI_API_KEY not found in environment variables")
        return False
    
    try:
        genai.configure(api_key=api_key)
        # Use Gemini 2.5 Flash (latest stable model)
        model_name = 'gemini-2.5-flash'
        gemini_model = genai.GenerativeModel(
            model_name,
            generation_config={
                'temperature': 0.7,
                'top_p': 0.95,
                'max_output_tokens': 1024
            }
        )
        logger.info(f"[OK] Gemini model initialized: {model_name}")
        logger.info(f"[OK] API Key: {api_key[:15]}...")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Gemini: {e}")
        return False

# Initialize Gemini on startup
gemini_initialized = initialize_gemini()

# ============================================================================
# CROSS-SELL RECOMMENDATION ENGINE
# ============================================================================
def generate_cross_sell_recommendations(product_name: str, limit: int = 3) -> dict:
    """
    Generate cross-sell recommendations using Gemini 2.5 Flash
    
    Args:
        product_name: Product name/type (e.g., 'laptop', 'mouse')
        limit: Number of recommendations (0-5)
        
    Returns:
        dict with recommendations list
    """
    if not gemini_initialized or not gemini_model:
        raise Exception("Gemini AI not initialized. Check GEMINI_API_KEY environment variable.")
    
    # Enforce limit between 0 and 5
    limit = max(0, min(limit, 5))
    
    if limit == 0:
        return {"recommendations": []}
    
    # Create prompt for Gemini
    prompt = f"""You are a product recommendation expert. A customer is viewing/purchasing a "{product_name}".

Generate {limit} cross-sell product recommendations that are commonly bought together with this product.

CRITICAL: Return ONLY valid JSON, no markdown, no code blocks, no extra text.

Format:
{{
  "recommendations": [
    {{
      "product_name": "Product Name",
      "reason": "Brief reason why this pairs well",
      "category": "Product Category",
      "estimated_price": "$XX.XX"
    }}
  ]
}}

Rules:
- Return exactly {limit} recommendations
- Use double quotes for all strings, no single quotes
- Reason should be 1 concise sentence
- Make realistic, practical suggestions
- Return ONLY the JSON object, nothing else"""
    
    try:
        logger.info(f"Requesting {limit} recommendations for: {product_name}")
        response = gemini_model.generate_content(prompt)
        
        # Parse JSON response
        response_text = response.text.strip()
        logger.info(f"Raw response length: {len(response_text)} chars")
        
        # Clean up response - remove markdown code blocks
        if response_text.startswith('```json'):
            response_text = response_text.split('```json', 1)[1].split('```', 1)[0].strip()
        elif response_text.startswith('```'):
            response_text = response_text.split('```', 1)[1].split('```', 1)[0].strip()
        
        # Remove any trailing text after the JSON
        if '```' in response_text:
            response_text = response_text.split('```')[0].strip()
        
        # Find JSON object boundaries
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        if start_idx != -1 and end_idx != -1:
            response_text = response_text[start_idx:end_idx+1]
        
        # Additional JSON cleanup
        # Fix common issues: trailing commas, single quotes, missing commas
        import re
        response_text = re.sub(r',(\s*[}\]])', r'\1', response_text)  # Remove trailing commas
        response_text = response_text.replace("'", '"')  # Replace single quotes with double quotes
        
        logger.info(f"Cleaned response: {response_text[:200]}...")
        
        try:
            recommendations_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            # Last resort: try to fix missing commas between objects
            logger.warning(f"Initial JSON parse failed, attempting fixes: {e}")
            response_text = re.sub(r'\}(\s*)\{', r'},\1{', response_text)
            response_text = re.sub(r'\](\s*)\[', r'],\1[', response_text)
            recommendations_data = json.loads(response_text)
        
        # Validate structure
        if 'recommendations' not in recommendations_data:
            raise Exception("Invalid response format: missing 'recommendations' key")
        
        # Trim to exact limit
        recommendations_data['recommendations'] = recommendations_data['recommendations'][:limit]
        
        logger.info(f"Successfully generated {len(recommendations_data['recommendations'])} recommendations")
        return recommendations_data
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        logger.error(f"Response text: {response.text[:1000]}")
        raise Exception(f"Gemini returned invalid JSON: {str(e)}")
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/')
def index():
    """Serve the main UI"""
    return send_from_directory('ui', 'index.html')

@app.route('/ui/<path:filename>')
def serve_ui(filename):
    """Serve UI static files"""
    return send_from_directory('ui', filename)

@app.route('/api/recommend', methods=['POST'])
def recommend():
    """
    Main recommendation endpoint
    
    Expected JSON format:
    {
        "product_id": "laptop",
        "limit": 3,
        "session_id": "optional_session_id"
    }
    """
    try:
        # Parse JSON input
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "Request body must be valid JSON",
                "timestamp": datetime.now().isoformat()
            }), 400
        
        # Extract parameters
        product_id = data.get('product_id')
        if not product_id:
            return jsonify({
                "status": "error",
                "message": "Missing required field: product_id",
                "timestamp": datetime.now().isoformat()
            }), 400
        
        limit = data.get('limit', 3)
        session_id = data.get('session_id', 'default')
        
        # Validate limit
        if not isinstance(limit, int) or limit < 0 or limit > 5:
            return jsonify({
                "status": "error",
                "message": "Limit must be an integer between 0 and 5",
                "timestamp": datetime.now().isoformat()
            }), 400
        
        logger.info(f"Recommendation request for product: {product_id}, limit: {limit}")
        
        # Generate recommendations
        result = generate_cross_sell_recommendations(product_id, limit)
        
        # Build response
        response = {
            "status": "success",
            "product_id": product_id,
            "session_id": session_id,
            "limit": limit,
            "recommendations": result['recommendations'],
            "model": "gemini-2.5-flash",
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Successfully returned {len(result['recommendations'])} recommendations")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error in recommend endpoint: {e}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/status', methods=['GET'])
def status():
    """Get agent status"""
    return jsonify({
        "status": "active",
        "agent": "Cross-Sell Suggestion Agent",
        "model": "gemini-2.5-flash",
        "gemini_initialized": gemini_initialized,
        "version": "2.0-simplified",
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/api/search', methods=['POST'])
def search():
    """
    Search endpoint (kept for frontend compatibility)
    """
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        # Simply echo back that this is a search for compatibility
        return jsonify({
            "status": "success",
            "query": query,
            "message": "Search functionality - type product names in the recommend field",
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    if not gemini_initialized:
        print("\n" + "="*60)
        print("ERROR: Gemini AI not initialized!")
        print("="*60)
        print("Please set GEMINI_API_KEY in your .env file")
        print("="*60 + "\n")
    else:
        print("\n" + "="*60)
        print("Cross-Sell Suggestion Agent")
        print("="*60)
        print("[OK] Gemini 2.5 Flash initialized")
        print("[OK] Server starting on http://127.0.0.1:5000")
        print("[OK] Open http://127.0.0.1:5000 in your browser")
        print("="*60 + "\n")
        
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False
        )
