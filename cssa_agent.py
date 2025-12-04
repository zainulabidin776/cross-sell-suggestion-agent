"""
Cross-Sell Suggestion Agent (CSSA)
Team: Awaiz Ali Khan, Zain ul Abideen, Kamran Ali
Course: SE4002 - Software Project Management
Enhanced with Google Gemini AI
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
import uuid
from logging.handlers import RotatingFileHandler
import sqlite3
import jsonschema
from jsonschema import ValidationError

# Import Gemini AI integration
try:
    from gemini_ai import initialize_gemini, gemini_engine
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Gemini AI integration not available")

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

# Add rotating file handler to prevent unbounded log growth
rot_handler = RotatingFileHandler('cssa_agent.log', maxBytes=2 * 1024 * 1024, backupCount=5)
rot_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(rot_handler)

app = Flask(__name__)

# ============================================================================
# SHORT-TERM MEMORY SYSTEM
# ============================================================================
class ShortTermMemory:
    """Manages conversation context and recent interactions"""
    
    def __init__(self, max_size=100):
        self.memory = {}
        self.max_size = max_size
        
    def store(self, session_id: str, data: dict):
        """Store interaction data"""
        if session_id not in self.memory:
            self.memory[session_id] = []
        
        self.memory[session_id].append({
            'timestamp': datetime.now().isoformat(),
            'data': data
        })
        
        # Keep only recent interactions
        if len(self.memory[session_id]) > self.max_size:
            self.memory[session_id] = self.memory[session_id][-self.max_size:]
        
        logger.info(f"Stored memory for session {session_id}")
        # Persist to long-term memory if available
        try:
            ltm = globals().get('ltm')
            if ltm:
                ltm.persist_interaction(session_id, data)
        except Exception:
            logger.exception("Failed to persist to long-term memory")
    
    def retrieve(self, session_id: str, limit: int = 5) -> List[dict]:
        """Retrieve recent interactions"""
        if session_id in self.memory:
            return self.memory[session_id][-limit:]
        return []
    
    def clear(self, session_id: str):
        """Clear session memory"""
        if session_id in self.memory:
            del self.memory[session_id]
            logger.info(f"Cleared memory for session {session_id}")

# Initialize STM
stm = ShortTermMemory()

# ============================================================================
# PRODUCT DATABASE & RECOMMENDATION ENGINE
# ============================================================================
class ProductDatabase:
    """Loads product catalog from external API with local JSON fallback"""
    
    def __init__(self):
        """Initialize: try to load from products.json (cached from API), fallback to hardcoded"""
        self.products = {}
        self.transaction_patterns = {}
        
        # Try to load from cached JSON file
        if self._load_from_json():
            logger.info("[OK] Loaded products from cached JSON (products.json)")
        else:
            logger.warning("⚠ Failed to load from JSON, using fallback data")
            self._load_fallback_data()
        
        # Compute transaction patterns from products
        self._compute_transaction_patterns()
    
    def _load_from_json(self) -> bool:
        """Load products from products.json file"""
        try:
            json_path = os.path.join(os.path.dirname(__file__), 'products.json')
            if os.path.exists(json_path):
                with open(json_path, 'r') as f:
                    data = json.load(f)
                    self.products = data
                    logger.info(f"Loaded {len(self.products)} products from JSON")
                    return True
        except Exception as e:
            logger.exception(f"Error loading JSON: {e}")
        return False
    
    def _compute_transaction_patterns(self):
        """Compute confidence scores based on cross-sell relationships"""
        self.transaction_patterns = {}
        for product_id, product in self.products.items():
            if product.get('cross_sell'):
                cross_sells = product['cross_sell']
                # Simple pattern: equal confidence across cross-sells
                confidence = 0.8 if len(cross_sells) <= 2 else 0.7
                self.transaction_patterns[product_id] = {
                    cs: confidence for cs in cross_sells
                }
    
    def _load_fallback_data(self):
        """Hardcoded fallback data if JSON not available"""
        self.products = {
            "laptop": {
                "id": "P001",
                "name": "Professional Laptop",
                "category": "Electronics",
                "price": 899.99,
                "cross_sell": ["mouse", "laptop_bag", "usb_hub"]
            },
            "phone": {
                "id": "P002",
                "name": "Smartphone Pro",
                "category": "Electronics",
                "price": 699.99,
                "cross_sell": ["phone_case", "screen_protector", "wireless_charger"]
            },
            "camera": {
                "id": "P003",
                "name": "Digital Camera",
                "category": "Electronics",
                "price": 549.99,
                "cross_sell": ["memory_card", "camera_bag", "tripod"]
            },
            "mouse": {
                "id": "P004",
                "name": "Wireless Mouse",
                "category": "Accessories",
                "price": 29.99,
                "cross_sell": ["mousepad", "keyboard"]
            },
            "laptop_bag": {
                "id": "P005",
                "name": "Laptop Backpack",
                "category": "Accessories",
                "price": 49.99,
                "cross_sell": ["laptop_sleeve", "cable_organizer"]
            },
            "usb_hub": {
                "id": "P006",
                "name": "USB-C Hub",
                "category": "Accessories",
                "price": 39.99,
                "cross_sell": ["usb_cable", "power_adapter"]
            },
            "phone_case": {
                "id": "P007",
                "name": "Protective Phone Case",
                "category": "Accessories",
                "price": 19.99,
                "cross_sell": ["screen_protector", "popsocket"]
            },
            "screen_protector": {
                "id": "P008",
                "name": "Tempered Glass Screen Protector",
                "category": "Accessories",
                "price": 12.99,
                "cross_sell": ["phone_case", "cleaning_kit"]
            },
            "wireless_charger": {
                "id": "P009",
                "name": "Fast Wireless Charger",
                "category": "Accessories",
                "price": 34.99,
                "cross_sell": ["power_bank", "charging_cable"]
            }
        }
        
        # Fallback transaction patterns
        self.transaction_patterns = {
            "laptop": {"mouse": 0.85, "laptop_bag": 0.75, "usb_hub": 0.65},
            "phone": {"phone_case": 0.90, "screen_protector": 0.80, "wireless_charger": 0.60},
            "camera": {"memory_card": 0.88, "camera_bag": 0.70, "tripod": 0.55}
        }
    
    def get_product(self, product_id: str) -> Optional[dict]:
        """Get product details"""
        return self.products.get(product_id)
    
    def search_products(self, query: str) -> List[dict]:
        """Search products by name or category"""
        results = []
        query_lower = query.lower()
        for pid, product in self.products.items():
            if (query_lower in product['name'].lower() or 
                query_lower in product['category'].lower() or
                query_lower in pid):
                results.append({**product, 'product_id': pid})
        return results

# Initialize database
product_db = ProductDatabase()

# ============================================================================
# RECOMMENDATION ENGINE
# ============================================================================
class RecommendationEngine:
    """Pure Gemini 2.0 Flash recommendation engine - NO fallback, NO dummy data"""
    
    def __init__(self, product_db: ProductDatabase):
        self.db = product_db
        
    def generate_recommendations(self, 
                                 product_id: str, 
                                 user_id: Optional[str] = None,
                                 limit: int = 3) -> List[dict]:
        """Generate cross-sell recommendations using ONLY Gemini 2.0 Flash"""
        
        # Check Gemini availability at runtime (not at init)
        if not GEMINI_AVAILABLE:
            raise Exception("Gemini AI package not installed. Install: pip install google-generativeai")
        
        if not gemini_engine or not gemini_engine.enabled:
            raise Exception("Gemini AI not initialized. Set GEMINI_API_KEY environment variable.")
        
        # Enforce max limit of 5
        limit = min(max(limit, 1), 5)
        
        product = self.db.get_product(product_id)
        if not product:
            raise Exception(f"Product '{product_id}' not found in catalog. Check available products in /api/search")
        
        # Use ONLY Gemini 2.0 Flash - no fallback
        try:
            logger.info(f"Requesting {limit} recommendations from Gemini 2.0 Flash for product: {product_id}")
            
            recommendations = gemini_engine.generate_recommendations_from_catalog(
                product=product,
                all_products=self.db.products,
                limit=limit,
                user_id=user_id
            )
            
            if not recommendations:
                raise Exception("Gemini returned empty recommendations")
            
            logger.info(f"[OK] Generated {len(recommendations)} Gemini recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Gemini recommendation failed: {e}")
            raise

# Initialize Gemini AI (optional - requires GEMINI_API_KEY env variable)
if GEMINI_AVAILABLE:
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    if gemini_api_key:
        initialize_gemini(gemini_api_key)
        logger.info("[OK] Gemini AI enabled for enhanced recommendations")
    else:
        logger.info("Gemini API key not set. Set GEMINI_API_KEY environment variable to enable AI recommendations")
else:
    logger.info("Gemini AI package not installed. Using basic recommendations only")

# Initialize recommendation engine
rec_engine = RecommendationEngine(product_db)


# -----------------------------
# Long-Term Memory (SQLite)
# -----------------------------
class LongTermMemory:
    """Simple SQLite persistence for session interactions"""
    def __init__(self, db_path='cssa_memory.db'):
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at TEXT
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp TEXT,
                data TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def persist_interaction(self, session_id: str, data: dict):
        conn = self._connect()
        cur = conn.cursor()
        # ensure session exists
        cur.execute('SELECT 1 FROM sessions WHERE session_id = ?', (session_id,))
        if not cur.fetchone():
            cur.execute('INSERT INTO sessions(session_id, created_at) VALUES(?, ?)',
                        (session_id, datetime.now().isoformat()))

        cur.execute('INSERT INTO interactions(session_id, timestamp, data) VALUES(?, ?, ?)',
                    (session_id, datetime.now().isoformat(), json.dumps(data)))
        conn.commit()
        conn.close()

    def get_session(self, session_id: str):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute('SELECT timestamp, data FROM interactions WHERE session_id = ? ORDER BY id', (session_id,))
        rows = cur.fetchall()
        conn.close()
        return [{'timestamp': r[0], 'data': json.loads(r[1])} for r in rows]

    def list_sessions(self):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute('SELECT session_id, created_at FROM sessions ORDER BY created_at')
        rows = cur.fetchall()
        conn.close()
        return [{'session_id': r[0], 'created_at': r[1]} for r in rows]


# Initialize LTM
ltm = LongTermMemory()

# ============================================================================
# AGENT METADATA & REGISTRY INFO
# ============================================================================
AGENT_METADATA = {
    "agent_id": "cssa_001",
    "agent_name": "Cross-Sell Suggestion Agent",
    "version": "1.0.0",
    "team": ["Awaiz Ali Khan", "Zain ul Abideen", "Kamran Ali"],
    "capabilities": [
        "product_recommendation",
        "cross_sell_suggestion",
        "product_search"
    ],
    "endpoints": {
        "health": "/health",
        "recommend": "/api/recommend",
        "search": "/api/search",
        "status": "/api/status"
    }
}

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Supervisor monitoring"""
    return jsonify({
        "status": "healthy",
        "agent_id": AGENT_METADATA['agent_id'],
        "agent_name": AGENT_METADATA['agent_name'],
        "version": AGENT_METADATA['version'],
        "timestamp": datetime.now().isoformat(),
        "uptime": "active"
    }), 200

@app.route('/api/status', methods=['GET'])
def get_status():
    """Detailed status endpoint"""
    return jsonify({
        "agent_metadata": AGENT_METADATA,
        "status": "operational",
        "memory_sessions": len(stm.memory),
        "total_products": len(product_db.products),
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/api/recommend', methods=['POST'])
def recommend():
    """
    Main recommendation endpoint
    
    Expected JSON format:
    {
        "request_id": "uuid",
        "session_id": "session_123",
        "product_id": "laptop",
        "user_id": "user_456",
        "limit": 3
    }
    """
    try:
        # Robust JSON parsing: accept proper JSON Content-Type or raw JSON body
        data = None
        if request.is_json:
            data = request.get_json(silent=True)
        else:
            # Attempt to parse raw body as JSON for clients that didn't set header
            try:
                raw = request.data.decode('utf-8') if request.data else ''
                data = json.loads(raw) if raw else None
            except Exception:
                return jsonify({
                    "status": "error",
                    "message": "Request body must be valid JSON. Set Content-Type: application/json",
                    "timestamp": datetime.now().isoformat()
                }), 415

        # Validate payload against schema
        recommend_schema = {
            "type": "object",
            "properties": {
                "request_id": {"type": "string"},
                "session_id": {"type": "string"},
                "product_id": {"type": "string"},
                "user_id": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 5}
            },
            "required": ["product_id"],
            "additionalProperties": False
        }

        try:
            jsonschema.validate(instance=data or {}, schema=recommend_schema)
        except ValidationError as ve:
            return jsonify({
                "status": "error",
                "message": f"Invalid request: {ve.message}",
                "timestamp": datetime.now().isoformat()
            }), 400
        
        # Extract parameters
        request_id = data.get('request_id', str(uuid.uuid4()))
        session_id = data.get('session_id', str(uuid.uuid4()))
        product_id = data.get('product_id')
        user_id = data.get('user_id')
        limit = min(data.get('limit', 3), 5)  # Enforce max 5
        
        logger.info(f"Recommendation request: {request_id} for product: {product_id}")
        
        # Generate recommendations using ONLY Gemini 2.0 Flash
        recommendations = rec_engine.generate_recommendations(
            product_id=product_id,
            user_id=user_id,
            limit=limit
        )
        
        # Store in STM
        stm.store(session_id, {
            'request_id': request_id,
            'product_id': product_id,
            'recommendations': recommendations
        })
        
        # Prepare response
        response = {
            "status": "success",
            "request_id": request_id,
            "session_id": session_id,
            "agent_id": AGENT_METADATA['agent_id'],
            "product_id": product_id,
            "recommendations": recommendations,
            "model": "gemini-2.0-flash",
            "limit_enforced": limit,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Successfully processed request {request_id}")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error processing recommendation: {str(e)}", exc_info=True)
        error_message = str(e)
        hint = ""
        
        # Add helpful hints based on error type
        if "not found in catalog" in error_message:
            hint = "Use /api/search endpoint to find valid product IDs (e.g., fakestore_1, dummyjson_1)"
        elif "Gemini" in error_message:
            hint = "Check that GEMINI_API_KEY environment variable is set correctly"
        
        return jsonify({
            "status": "error",
            "message": error_message,
            "hint": hint if hint else None,
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/search', methods=['POST'])
def search_products():
    """
    Product search endpoint
    
    Expected JSON format:
    {
        "query": "laptop",
        "session_id": "session_123"
    }
    """
    try:
        # Robust JSON parsing for search endpoint as well
        data = None
        if request.is_json:
            data = request.get_json(silent=True)
        else:
            try:
                raw = request.data.decode('utf-8') if request.data else ''
                data = json.loads(raw) if raw else None
            except Exception:
                return jsonify({
                    "status": "error",
                    "message": "Request body must be valid JSON. Set Content-Type: application/json"
                }), 415

        # Validate payload against schema
        search_schema = {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "session_id": {"type": "string"}
            },
            "required": ["query"],
            "additionalProperties": False
        }

        try:
            jsonschema.validate(instance=data or {}, schema=search_schema)
        except ValidationError as ve:
            return jsonify({"status": "error", "message": f"Invalid request: {ve.message}"}), 400
        
        query = data.get('query')
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        logger.info(f"Search request for: {query}")
        
        # Search products
        results = product_db.search_products(query)
        
        # Store in STM
        stm.store(session_id, {
            'action': 'search',
            'query': query,
            'results_count': len(results)
        })
        
        return jsonify({
            "status": "success",
            "query": query,
            "results": results,
            "count": len(results),
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in search: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/registry', methods=['GET'])
def get_registry_info():
    """Return agent registration information for Supervisor"""
    return jsonify({
        "agent_metadata": AGENT_METADATA,
        "handshake_protocol": {
            "format": "JSON",
            "required_fields": ["request_id", "product_id"],
            "optional_fields": ["session_id", "user_id", "limit"]
        },
        "response_format": {
            "status": "success|error",
            "recommendations": "array of product objects",
            "timestamp": "ISO 8601 format"
        }
    }), 200


@app.route('/api/memory', methods=['GET'])
def list_memory_sessions():
    """List all stored sessions in long-term memory"""
    try:
        sessions = ltm.list_sessions()
        return jsonify({"status": "success", "sessions": sessions}), 200
    except Exception as e:
        logger.exception("Error listing memory sessions")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/memory/<session_id>', methods=['GET'])
def get_memory_session(session_id):
    """Return persisted interactions for a session"""
    try:
        data = ltm.get_session(session_id)
        return jsonify({"status": "success", "session_id": session_id, "interactions": data}), 200
    except Exception as e:
        logger.exception("Error fetching memory session")
        return jsonify({"status": "error", "message": str(e)}), 500


# Serve minimal UI (static files) for demo
@app.route('/', methods=['GET'])
def index():
    ui_dir = os.path.join(os.path.dirname(__file__), 'ui')
    return send_from_directory(ui_dir, 'index.html')


@app.route('/ui/<path:filename>', methods=['GET'])
def ui_files(filename):
    ui_dir = os.path.join(os.path.dirname(__file__), 'ui')
    return send_from_directory(ui_dir, filename)


@app.route('/openapi.json', methods=['GET'])
def openapi_spec():
    """Serve OpenAPI spec for Swagger UI"""
    spec_path = os.path.join(os.path.dirname(__file__), 'openapi.json')
    with open(spec_path, 'r') as f:
        return jsonify(json.load(f)), 200

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================
if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Starting Cross-Sell Suggestion Agent")
    logger.info(f"Agent ID: {AGENT_METADATA['agent_id']}")
    logger.info(f"Version: {AGENT_METADATA['version']}")
    logger.info("=" * 60)
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )