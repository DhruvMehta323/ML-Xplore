from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
import sqlite3
import jwt
import os
from dotenv import load_dotenv
import datetime
from functools import wraps

load_dotenv()

app = Flask(__name__)
CORS(app)

JWT_SECRET = os.getenv('JWT_SECRET', 'secret-key-change-in-production')
DATABASE_PATH = os.getenv('DATABASE_PATH', '../data/database.db')
DATABASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), DATABASE_PATH))

# ============================================================================
# AUTHENTICATION DECORATORS
# ============================================================================

def token_required(f):
    """Decorator to require JWT authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        
        try:
            token = token.split(" ")[1] if " " in token else token
            decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            request.user = decoded
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        return f(*args, **kwargs)
    return decorated

# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.json
    
    if not data:
        return jsonify({"error": "Request body is required"}), 400
    
    email = data.get('email')
    name = data.get('name', '')
    password = data.get('password')
    preferences = data.get('preferences', [])
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    if not isinstance(preferences, list):
        return jsonify({"error": "Preferences should be a list"}), 400
    
    # Convert preferences to lowercase CSV
    preference_csv = ",".join([
        pref.strip().lower().rstrip('s') for pref in preferences
    ])
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (email, name, password, preferences) VALUES (?, ?, ?, ?)",
            (email, name, password, preference_csv)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            "message": "User registered successfully",
            "user_id": user_id
        }), 201
        
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 409
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token"""
    data = request.json
    
    if not data:
        return jsonify({"error": "Request body is required"}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, email, name FROM users WHERE email = ? AND password = ?",
            (email, password)
        )
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return jsonify({"error": "Invalid email or password"}), 401
        
        user_id, email, name = user
        token = jwt.encode({
            "user_id": user_id,
            "email": email,
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
        }, JWT_SECRET, algorithm="HS256")
        
        return jsonify({
            "token": token,
            "user": {
                "id": user_id,
                "email": email,
                "name": name
            }
        }), 200
        
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@app.route('/api/user', methods=['GET'])
@token_required
def get_user():
    """Get current user details"""
    user = request.user
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, email, name, preferences FROM users WHERE id = ?",
            (user["user_id"],)
        )
        user_data = cursor.fetchone()
        conn.close()
        
        if not user_data:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "id": user_data[0],
            "email": user_data[1],
            "name": user_data[2],
            "preferences": user_data[3].split(',') if user_data[3] else []
        }), 200
        
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# ============================================================================
# SEARCH ROUTES
# ============================================================================

@app.route('/api/search', methods=['GET'])
def search():
    """Search resources using TF-IDF"""
    query = request.args.get('query', '')
    tags_filter = request.args.getlist('tags[]')
    
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        sql_query = "SELECT description, summary, url, title, tags, popularity_score FROM resources"
        
        if tags_filter:
            tags_condition = " OR ".join([f"tags LIKE '%{tag}%'" for tag in tags_filter])
            sql_query += " WHERE " + tags_condition
        
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return jsonify([]), 200
        
        descriptions, summaries, urls, titles, tags, popularity_scores = zip(*rows)
        
        query_lower = query.lower()
        
        # Title matching scores (exact and partial matches)
        title_scores = []
        for title in titles:
            title_lower = (title or '').lower()
            
            # Exact match in title = very high score
            if query_lower in title_lower:
                title_scores.append(1.0)
            # Check for word matches
            else:
                query_words = query_lower.split()
                title_words = title_lower.split()
                matches = sum(1 for qw in query_words if any(qw in tw for tw in title_words))
                title_scores.append(matches / max(len(query_words), 1))

        combined_texts = [
            (desc if desc else "") + " " + (summ if summ else "")
            for desc, summ in zip(descriptions, summaries)
        ]
        
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(combined_texts)
        query_vec = vectorizer.transform([query])
        content_scores = (tfidf_matrix @ query_vec.T).toarray().ravel()
        
        # Normalize scores
        if content_scores.any():
            max_content = max(content_scores)
            if max_content > 0:
                content_scores = [score / max_content for score in content_scores]
        
        if popularity_scores:
            max_popularity = max(popularity_scores)
            if max_popularity > 0:
                popularity_scores = [score / max_popularity for score in popularity_scores]
        
        # Combine scores (80% relevance, 20% popularity)
        combined_scores = [
            0.5 * title_score + 0.3 * content_score + 0.2 * pop_score
            for title_score, content_score, pop_score 
            in zip(title_scores, content_scores, popularity_scores)
        ]
        
        results = [
            {
                "url": url,
                "title": title,
                "description": description,
                "tags": tag,
                "score": score
            }
            for url, title, description, tag, score in zip(urls, titles, descriptions, tags, combined_scores)
        ]
        
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return jsonify(results[:20]), 200
        
    except Exception as e:
        return jsonify({"error": f"Search error: {str(e)}"}), 500

# ============================================================================
# RECOMMENDATION ROUTES
# ============================================================================

@app.route('/api/recommendations', methods=['GET'])
@token_required
def get_recommendations():
    """Get personalized recommendations based on user preferences"""
    user = request.user
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT preferences FROM users WHERE id = ?", (user["user_id"],))
        user_data = cursor.fetchone()
        
        if not user_data or not user_data[0]:
            return jsonify([]), 200
        
        user_preferences = user_data[0].split(',')
        
        cursor.execute("""
            SELECT id, url, title, description, tags, popularity_score 
            FROM resources 
            WHERE url NOT LIKE '%privacy%' 
            AND url NOT LIKE '%copyright%'
            AND url NOT LIKE '%terms%'
            AND url NOT LIKE '%policy%'
        """)
        resources = cursor.fetchall()
        conn.close()
        
        scored_resources = []
        for resource in resources:
            resource_tags = [tag.strip() for tag in resource[4].split(',')]
            
            # Calculate tag match score
            matching_tags = set(resource_tags) & set(user_preferences)
            tag_score = len(matching_tags)
            
            # Weighted score: 50% tag match, 50% popularity
            weighted_score = tag_score * 0.5 + resource[5] * 0.5
            
            scored_resources.append({
                'url': resource[1],
                'title': resource[2],
                'description': resource[3],
                'tags': resource[4],
                'popularity_score': resource[5],
                'score': weighted_score
            })
        
        scored_resources.sort(key=lambda x: x['score'], reverse=True)
        
        return jsonify(scored_resources[:20]), 200
        
    except Exception as e:
        return jsonify({"error": f"Recommendation error: {str(e)}"}), 500

# ============================================================================
# HISTORY ROUTES
# ============================================================================

@app.route('/api/history', methods=['GET'])
@token_required
def get_history():
    """Get user's browsing history"""
    user = request.user
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT usi.resource_url, r.title, r.description, usi.timestamp
            FROM user_source_interaction usi
            LEFT JOIN resources r ON usi.resource_url = r.url
            WHERE usi.user_id = ?
            ORDER BY usi.timestamp DESC
            LIMIT 50
        """, (user["user_id"],))
        interactions = cursor.fetchall()
        conn.close()
        
        history = [
            {
                "url": interaction[0],
                "title": interaction[1] or "Unknown",
                "description": interaction[2] or "",
                "timestamp": interaction[3]
            }
            for interaction in interactions
        ]
        
        return jsonify(history), 200
        
    except Exception as e:
        return jsonify({"error": f"History error: {str(e)}"}), 500

@app.route('/api/history', methods=['POST'])
@token_required
def add_to_history():
    """Add a resource to user's history"""
    user = request.user
    data = request.json
    
    if not data:
        return jsonify({"error": "Request body is required"}), 400
    
    resource_url = data.get('resource_url')
    
    if not resource_url:
        return jsonify({"error": "Resource URL is required"}), 400
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user_source_interaction (user_id, resource_url) VALUES (?, ?)",
            (user["user_id"], resource_url)
        )
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Added to history"}), 201
        
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# ============================================================================
# ADMIN ROUTES
# ============================================================================

@app.route('/api/admin/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM resources")
        total_resources = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM links")
        total_links = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user_source_interaction")
        total_interactions = cursor.fetchone()[0]
        
        cursor.execute("SELECT tags, COUNT(*) as count FROM resources GROUP BY tags ORDER BY count DESC LIMIT 10")
        tag_distribution = [{"tag": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            "total_resources": total_resources,
            "total_links": total_links,
            "total_users": total_users,
            "total_interactions": total_interactions,
            "tag_distribution": tag_distribution
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Stats error: {str(e)}"}), 500

@app.route('/api/admin/resources', methods=['GET'])
def get_all_resources():
    """Get all resources with pagination"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    offset = (page - 1) * per_page
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT url, title, description, tags, popularity_score, last_crawled
            FROM resources
            ORDER BY last_crawled DESC
            LIMIT ? OFFSET ?
        """, (per_page, offset))
        
        resources = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) FROM resources")
        total = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            "resources": [
                {
                    "url": r[0],
                    "title": r[1],
                    "description": r[2],
                    "tags": r[3],
                    "popularity_score": r[4],
                    "last_crawled": r[5]
                }
                for r in resources
            ],
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Error fetching resources: {str(e)}"}), 500

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "API is running"}), 200

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("ML Resource Discovery API")
    print("=" * 60)
    print(f"Database: {DATABASE_PATH}")
    print("Starting server...")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)