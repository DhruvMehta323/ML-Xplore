# 🧠 ML-Xplore

**Intelligent Machine Learning Resource Discovery Platform**

A full-stack web application that intelligently discovers, crawls, indexes, and recommends machine learning resources from across the web. Built with advanced search algorithms (TF-IDF), graph-based ranking (PageRank), and personalized recommendations.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![React](https://img.shields.io/badge/React-18.2-61dafb.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📸 Screenshots

### Search Results

#### Common Search: "Deep Learning"

<img width="1176" height="778" alt="image" src="https://github.com/user-attachments/assets/c21fee8c-65e1-4816-b145-80cd2e126c7b" />

**Results shown:**
- ✅ More closely aligned results with higher confidence level / matching scores

---

#### Niche Search: "Multimodal LLMs"

<img width="1125" height="818" alt="image" src="https://github.com/user-attachments/assets/6ead6da6-64b3-43c8-97b4-32102d5f72fc" />


**Results shown:**
- ✅ 20 resources (demonstrates niche topic coverage)
- ✅ Recent research papers from ArXiv(Google Deepmind)
- ✅ Hugging Face models and papers
- ✅ Results with low confidence level because of no complete matching due to limited data/ links that is scraped

---


### Personalized Recommendations

> *Screenshot of recommendations page with user preferences shown*

<img width="1155" height="827" alt="image" src="https://github.com/user-attachments/assets/3dd666c6-7922-4cb7-9dfa-80cffde29110" />

**How it works:**
1. User preferences: `dataset`, `research paper`, `model`
2. System matches resources with these tags
3. Combines tag matching (50%) + popularity (50%)
4. Shows top 20 most relevant resources

**Example shown:**
- User interested in: Datasets, Research Papers
- Top recommendations:
  - Kaggle datasets (90% match)
  - ArXiv papers (85% match)
  - Papers with Code (80% match)

---

### History Tracking

> *Screenshot of history page showing timeline*

<img width="1092" height="823" alt="image" src="https://github.com/user-attachments/assets/34ab0740-57e3-4c52-aa94-4dd424976fec" />

**Features shown:**
- ✅ Timeline view of visited resources
- ✅ Date stamps for each interaction
- ✅ Quick re-access to previous resources
- ✅ Organized by most recent first

---

### Admin Dashboard

> *Screenshot of admin dashboard with statistics*

<img width="1119" height="814" alt="image" src="https://github.com/user-attachments/assets/ebe04026-33a2-40db-a745-1188c28c9274" />


**Statistics displayed:**
- 📊 Total Resources: 1787
- 🔗 Total Links: 121798
- 👥 Total Users: 1
- 📈 Total Interactions: 15

## 🎯 Key Features

### 🔍 **Intelligent Search**
- **Title-Weighted Ranking**: 50% title relevance + 30% content similarity + 20% popularity
- **TF-IDF Algorithm**: Advanced text matching for content relevance
- **Tag-Based Filtering**: Filter by type (dataset, model, article, research paper, code, documentation)
- **Fast Results**: <100ms average query time

### 🎯 **Personalized Recommendations**
- **User Preference Matching**: Analyzes user-selected interests
- **Hybrid Scoring**: Combines preference matching with popularity
- **Dynamic Updates**: Recommendations improve with user interactions

### 📊 **Comprehensive Crawling**
- **Multi-Source**: 24+ high-quality ML sources
- **Breadth-First Search**: Efficient link discovery
- **Smart Tagging**: URL and content-based categorization
- **100,000+ Links**: Massive resource graph

### 🎨 **Modern UI/UX**
- **React 18**: Fast, responsive interface
- **Real-time Search**: Instant results as you type
- **Mobile Responsive**: Works on all devices
- **Dark Theme**: Easy on the eyes

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE (React)                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │  Search  │ │   Recs   │ │ History  │ │  Admin   │          │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘          │
└───────┼───────────┼──────────┼──────────┼─────────────────────┘
        │           │          │          │
        └───────────┴──────────┴──────────┘
                    │
        ┌───────────▼──────────┐
        │   REST API (Flask)    │
        │   JWT Authentication  │
        └───────────┬──────────┘
                    │
        ┌───────────▼──────────────────────────────────────┐
        │         SEARCH & RANKING ENGINE                   │
        │  ┌──────────┐ ┌──────────┐ ┌──────────┐         │
        │  │  TF-IDF  │ │ PageRank │ │  Hybrid  │         │
        │  │ Matching │ │  Scoring │ │  Ranking │         │
        │  └──────────┘ └──────────┘ └──────────┘         │
        └───────────┬──────────────────────────────────────┘
                    │
        ┌───────────▼──────────────────────────────────────┐
        │         DATA PROCESSING PIPELINE                  │
        │  ┌──────────┐ ┌──────────┐ ┌──────────┐         │
        │  │ Crawler  │ │ Indexer  │ │PageRank  │         │
        │  │   (BFS)  │ │ (TF-IDF) │ │(Iterative)│        │
        │  └──────────┘ └──────────┘ └──────────┘         │
        └───────────┬──────────────────────────────────────┘
                    │
        ┌───────────▼──────────────────────────────────────┐
        │              SQLite DATABASE                      │
        │                                                    │
        │  ┌──────────┐ ┌──────────┐ ┌──────────┐         │
        │  │Resources │ │  Links   │ │  Users   │         │
        │  └──────────┘ └──────────┘ └──────────┘         │
        │                                                    │
        │  ┌──────────────────────────────────┐            │
        │  │    User-Resource Interactions     │            │
        │  └──────────────────────────────────┘            │
        └───────────────────────────────────────────────────┘
```

---

## 🧮 Core Algorithms

### 1. Web Crawling (BFS Algorithm)

**Algorithm**: Breadth-First Search (BFS) with depth limiting

```python
# Simplified crawling algorithm
def crawl_site(start_url, max_depth):
    queue = deque([(start_url, 1)])  # (url, depth)
    visited = set()
    
    while queue:
        url, depth = queue.popleft()  # BFS: process in order
        
        if url in visited or depth > max_depth:
            continue
            
        visited.add(url)
        
        # Extract page content
        page = fetch_page(url)
        title, description, links = extract_data(page)
        tags = classify_resource(page, url)
        
        # Store in database
        store_resource(url, title, description, tags)
        
        # Add links to queue for BFS exploration
        for link in links:
            if link not in visited:
                store_link(url, link)  # Build link graph
                queue.append((link, depth + 1))
```

**Why BFS?**
- ✅ Explores resources level-by-level
- ✅ Finds popular resources first (closer to seed URLs)
- ✅ Better for web graphs than DFS
- ✅ Ensures broad coverage before going deep

**Depth Strategy:**
```
Depth 1: Seed URLs (landing pages)          →  24 pages
Depth 2: Direct links (main categories)      →  ~500 pages
Depth 3: Sub-categories (specific topics)    →  ~2,000 pages
Depth 4: Individual resources (papers, etc)  →  ~10,000 pages
```

---

### 2. TF-IDF Indexing

**Algorithm**: Term Frequency - Inverse Document Frequency

```python
# TF-IDF summary generation
def generate_summary(title, description, content):
    # Combine all text (title weighted more)
    full_text = f"{title} {title} {description} {content}"
    
    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer(
        max_features=25,      # Top 25 keywords
        stop_words='english'  # Remove common words
    )
    
    tfidf_matrix = vectorizer.fit_transform([full_text])
    
    # Get top keywords
    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.toarray()[0]
    
    # Sort by importance
    top_indices = scores.argsort()[-25:][::-1]
    keywords = [feature_names[i] for i in top_indices]
    
    return " ".join(keywords)  # Searchable summary
```

**Why TF-IDF?**
- ✅ Identifies important keywords (high TF)
- ✅ Reduces weight of common words (high DF)
- ✅ Creates searchable summaries
- ✅ Fast similarity computation

**Example:**
```
Title: "Understanding Neural Networks for Beginners"
TF-IDF Keywords: neural networks understanding beginners
                 backpropagation layers training deep
                 learning architecture optimization
```

---

### 3. PageRank Calculation

**Algorithm**: Iterative PageRank with damping factor

```python
# Simplified PageRank
def calculate_pagerank(links, damping=0.85, iterations=20):
    # Initialize: all pages start with rank 1.0
    pages = get_all_pages()
    pagerank = {page: 1.0 for page in pages}
    
    # Build graph structure
    inbound_links = build_inbound_map(links)
    outbound_counts = count_outbound_links(links)
    
    # Iterate to convergence
    for iteration in range(iterations):
        new_ranks = {}
        
        for page in pages:
            # Sum contributions from linking pages
            rank_sum = 0
            for linking_page in inbound_links[page]:
                rank_sum += pagerank[linking_page] / outbound_counts[linking_page]
            
            # Apply damping factor
            new_ranks[page] = (1 - damping) + damping * rank_sum
        
        pagerank = new_ranks
    
    return pagerank
```

**Formula:**
```
PR(A) = (1 - d) + d × Σ(PR(Ti) / C(Ti))

where:
- PR(A) = PageRank of page A
- d = damping factor (0.85)
- Ti = pages that link to A
- C(Ti) = number of outbound links from Ti
- Iterations = 20 (convergence)
```

**Why PageRank?**
- ✅ Identifies authoritative resources
- ✅ Link-based quality signal
- ✅ Resistant to manipulation
- ✅ Proven algorithm (used by Google)

**Example:**
```
Resource A: 100 inbound links, PR = 2.5  →  High authority
Resource B: 10 inbound links,  PR = 1.2  →  Medium authority
Resource C: 1 inbound link,    PR = 0.8  →  Lower authority
```

---

### 4. Search Ranking (Hybrid Algorithm)

**Algorithm**: Multi-factor ranking combining relevance and authority

```python
# Search ranking algorithm
def search_and_rank(query):
    resources = fetch_all_resources()
    
    # Component 1: Title Matching (50% weight)
    title_scores = []
    for resource in resources:
        if query.lower() in resource.title.lower():
            title_scores.append(1.0)  # Exact match
        else:
            # Partial word matching
            query_words = query.lower().split()
            title_words = resource.title.lower().split()
            matches = sum(1 for qw in query_words 
                         if any(qw in tw for tw in title_words))
            title_scores.append(matches / len(query_words))
    
    # Component 2: Content Relevance (30% weight)
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(
        [r.description + " " + r.summary for r in resources]
    )
    query_vector = vectorizer.transform([query])
    content_scores = (tfidf_matrix @ query_vector.T).toarray().ravel()
    
    # Normalize
    content_scores = content_scores / max(content_scores)
    
    # Component 3: Popularity (20% weight)
    popularity_scores = [r.popularity_score for r in resources]
    popularity_scores = [s / max(popularity_scores) for s in popularity_scores]
    
    # Combine with weights
    final_scores = [
        0.5 * title + 0.3 * content + 0.2 * popularity
        for title, content, popularity 
        in zip(title_scores, content_scores, popularity_scores)
    ]
    
    # Sort by score
    ranked_results = sorted(
        zip(resources, final_scores),
        key=lambda x: x[1],
        reverse=True
    )
    
    return ranked_results[:20]  # Top 20
```

**Why This Weighting?**
- **50% Title**: Most important signal for relevance
- **30% Content**: Ensures topical match
- **20% Popularity**: Quality signal, but not dominant

**Example Scoring:**
```
Query: "reinforcement learning"

Resource A:
  Title: "Reinforcement Learning Tutorial"  →  1.0 (exact match)
  Content: High similarity                   →  0.9
  Popularity: Medium                         →  0.5
  Final Score: 0.5×1.0 + 0.3×0.9 + 0.2×0.5 = 0.87 ✅ Rank #1

Resource B:
  Title: "Machine Learning Overview"        →  0.3 (partial match)
  Content: Medium similarity                 →  0.6
  Popularity: High                           →  0.9
  Final Score: 0.5×0.3 + 0.3×0.6 + 0.2×0.9 = 0.51   Rank #5
```

---

### 5. Recommendation Algorithm

**Algorithm**: Preference-based collaborative filtering

```python
# Recommendation algorithm
def get_recommendations(user):
    # Get user preferences
    user_prefs = user.preferences.split(',')  # e.g., ['dataset', 'model']
    
    # Fetch all resources
    resources = fetch_all_resources()
    
    scored_resources = []
    for resource in resources:
        # Get resource tags
        resource_tags = resource.tags.split(',')
        
        # Calculate tag match score
        matching_tags = set(resource_tags) & set(user_prefs)
        tag_score = len(matching_tags)  # 0, 1, 2, ...
        
        # Get popularity score
        popularity_score = resource.popularity_score
        
        # Hybrid score: 50% preference match + 50% popularity
        final_score = 0.5 * tag_score + 0.5 * popularity_score
        
        scored_resources.append((resource, final_score))
    
    # Sort by score
    scored_resources.sort(key=lambda x: x[1], reverse=True)
    
    return scored_resources[:20]  # Top 20
```

**How It Works:**

**Example: User Profile**
```
Preferences: ["dataset", "research paper", "model"]
```

**Resource Evaluation:**
```
Resource A:
  Tags: "dataset", "research paper"
  Matching tags: 2
  Popularity: 1.5
  Score: 0.5×2 + 0.5×1.5 = 1.75  ✅ Highly recommended

Resource B:
  Tags: "article", "tutorial"
  Matching tags: 0
  Popularity: 2.0
  Score: 0.5×0 + 0.5×2.0 = 1.0    Medium recommendation

Resource C:
  Tags: "dataset"
  Matching tags: 1
  Popularity: 0.5
  Score: 0.5×1 + 0.5×0.5 = 0.75   Lower recommendation
```

**Recommendation Strategy:**
1. **High Match + High Popularity** → Top recommendations
2. **High Match + Low Popularity** → Good finds (hidden gems)
3. **Low Match + High Popularity** → Still shown (exploration)
4. **Low Match + Low Popularity** → Filtered out

---

## 🔄 Complete Data Pipeline

### Phase 1: Data Collection (Crawling)

```
1. Seed URLs (start_urls)
   ├─→ ArXiv categories
   ├─→ Kaggle listings  
   ├─→ Medium topics
   └─→ Hugging Face collections

2. BFS Crawling
   ├─→ Depth 1: Landing pages
   ├─→ Depth 2: Category pages
   ├─→ Depth 3: Resource listings
   └─→ Depth 4: Individual resources

3. Data Extraction
   ├─→ Title (from <title> tag)
   ├─→ Description (from <meta> tag)
   ├─→ Content (from <body> text)
   └─→ Links (from <a> tags)

4. Link Graph Construction
   ├─→ Store: (source_url, destination_url)
   └─→ Build directed graph

5. Tag Assignment
   ├─→ URL pattern matching
   └─→ Content keyword analysis
```

**Output:**
- Resources table: 3,000-4,000 entries
- Links table: 100,000-150,000 entries

---

### Phase 2: Indexing (TF-IDF)

```
1. Load Resources
   └─→ Get: title, description, (future: content)

2. Text Preprocessing
   ├─→ Combine: title + description + content
   ├─→ Lowercase
   ├─→ Remove stop words
   └─→ Tokenize

3. TF-IDF Calculation
   ├─→ Term Frequency (TF)
   ├─→ Inverse Document Frequency (IDF)
   └─→ TF-IDF = TF × IDF

4. Keyword Extraction
   ├─→ Sort terms by TF-IDF score
   ├─→ Select top 25 keywords
   └─→ Create searchable summary

5. Database Update
   └─→ Store summary in resources table
```

**Output:**
- Each resource has searchable summary
- Ready for fast similarity matching

---

### Phase 3: Ranking (PageRank)

```
1. Build Link Graph
   ├─→ Nodes: All resources
   └─→ Edges: Links between resources

2. Initialize Ranks
   └─→ All pages start with rank = 1.0

3. Iterate (20 times)
   ├─→ For each page:
   │   ├─→ Calculate incoming rank contributions
   │   ├─→ Apply damping factor (0.85)
   │   └─→ Update rank
   └─→ Converge to stable values

4. Normalize Scores
   └─→ Scale to 0-10 range

5. Database Update
   └─→ Store popularity_score in resources table
```

**Output:**
- Each resource has authority score
- High-quality resources ranked higher

---

### Phase 4: Search (Real-time)

```
1. Receive Query
   └─→ User enters: "neural networks"

2. Title Matching
   ├─→ Exact match detection
   └─→ Partial word matching

3. TF-IDF Similarity
   ├─→ Convert query to TF-IDF vector
   ├─→ Compare with all resource summaries
   └─→ Calculate cosine similarity

4. Retrieve Popularity
   └─→ Get PageRank scores

5. Hybrid Ranking
   ├─→ Combine: 50% title + 30% content + 20% popularity
   └─→ Sort by final score

6. Return Results
   └─→ Top 20 resources
```

**Response Time:** <100ms

---

### Phase 5: Recommendations (User-based)

```
1. Load User Profile
   └─→ preferences = ["dataset", "model"]

2. Fetch Resources
   └─→ All resources from database

3. Tag Matching
   ├─→ Count matching tags
   └─→ resource_tags ∩ user_preferences

4. Combine with Popularity
   └─→ score = 0.5 × matches + 0.5 × popularity

5. Rank and Filter
   ├─→ Sort by score
   └─→ Return top 20

6. Track Interaction
   └─→ When user clicks → store in history
```

**Updates:** Dynamic based on user behavior

---

## 📊 Data Sources

| Source | Type | Depth | Target | Coverage |
|--------|------|-------|--------|----------|
| **ArXiv** | Papers | 4 | 400 | cs.LG, cs.AI, cs.CV, cs.CL |
| **Hugging Face** | Models/Datasets | 3 | 400 | Models, Datasets, Papers |
| **Papers with Code** | Papers/Datasets | 4 | 300 | Methods, Datasets, SOTA |
| **Kaggle** | Datasets/Models | 3 | 250 | Datasets, Models |
| **Medium** | Articles | 4 | 450 | ML, DL, AI topics |
| **Towards Data Science** | Articles | 4 | 400 | ML, DL, AI |
| **ML Mastery** | Tutorials | 3 | 200 | DL, NLP, ML |
| **Analytics Vidhya** | Articles | 3 | 100 | Blog posts |
| **KDnuggets** | Articles | 3 | 100 | ML news |
| **OpenAI** | Research | 3 | 80 | Research blog |
| **Google AI** | Research | 3 | 100 | AI blog |
| **DeepMind** | Research | 3 | 80 | Research blog |

**Total Target:** 3,000+ resources, 100,000+ links

---

## 📁 Project Structure

```
ml-resource-app/
├── backend/                          # Flask API Server
│   ├── app.py                       # REST API with search & recommendations
│   ├── mega_crawler.py              # BFS crawler (100k+ links)
│   ├── topic_crawler.py             # Niche topic crawler
│   ├── indexer.py                   # TF-IDF summary generator
│   ├── pagerank.py                  # PageRank calculator
│   ├── db.py                        # Database schema setup
│   ├── check_db.py                  # Diagnostics tool
│   ├── test_crawler.py              # Crawler testing
│   └── requirements.txt             # Python dependencies
│
├── frontend/                         # React Application
│   ├── src/
│   │   ├── components/              # Reusable components
│   │   │   ├── Navbar.jsx          # Navigation bar
│   │   │   └── ResourceCard.jsx    # Resource display card
│   │   ├── pages/                   # Main pages
│   │   │   ├── Login.jsx           # Authentication
│   │   │   ├── Register.jsx        # User registration
│   │   │   ├── Search.jsx          # Search interface
│   │   │   ├── Recommendations.jsx # Personalized recommendations
│   │   │   ├── History.jsx         # User history
│   │   │   └── Admin.jsx           # Admin dashboard
│   │   ├── styles/                  # CSS styles
│   │   ├── api.js                   # API client (Axios)
│   │   ├── App.jsx                  # Root component
│   │   └── main.jsx                 # Entry point
│   ├── package.json
│   └── vite.config.js
│
├── data/                         # SQLite database
│   └── database.db                  # Auto-generated
│
├── README.md                         # This file
├── .gitignore                        # Git ignore rules
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- Chrome/Chromium browser

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/ML-Xplore.git
cd ML-Xplore

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# Initialize database
python db.py

# Populate database (choose one):

# Option 1: Quick test (100 resources, 10 min)
python targeted_crawler.py  # Select a few sources

# Option 2: Full crawl (3000+ resources, 3-5 hours)
python mega_crawler.py      # Recommended for 100k+ links
python topic_crawler.py     # Add niche topics

# Generate search indices
python indexer.py           # TF-IDF summaries
python pagerank.py          # Popularity scores

# Verify
python check_db.py

# Start backend
python app.py              # http://localhost:5000

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev                # http://localhost:3000
```

### Access

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API Health**: http://localhost:5000/api/health

---

## 🎯 Usage Examples

### 1. Search for Resources

```bash
# Via API
curl "http://localhost:5000/api/search?query=deep+learning"

# With tag filter
curl "http://localhost:5000/api/search?query=mnist&tags[]=dataset"
```

**Response:**
```json
[
  {
    "url": "https://arxiv.org/abs/...",
    "title": "Deep Learning for Computer Vision",
    "description": "Comprehensive survey of deep learning...",
    "tags": "research paper, article",
    "score": 0.87
  },
  ...
]
```

### 2. Get Recommendations

```bash
# Requires authentication
curl -H "Authorization: Bearer <token>" \
     http://localhost:5000/api/recommendations
```

### 3. Register User

```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure123",
    "name": "John Doe",
    "preferences": ["dataset", "research paper", "model"]
  }'
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Check database status
python check_db.py

# Test API endpoints
curl http://localhost:5000/api/health
curl http://localhost:5000/api/admin/stats
```

### Frontend Tests

```bash
cd frontend
npm test  # Run test suite (if configured)
```

---

## 📈 Performance Metrics

### Crawling Performance
- **Speed**: 20-30 pages/minute
- **Memory**: ~300MB during crawling
- **Network**: Depends on connection
- **Time**: 3-5 hours for 3,000+ resources

### Search Performance
- **Query Time**: <100ms average
- **Index Size**: ~50MB for 3,000 resources
- **Concurrent Users**: Supports 50+ simultaneous searches

### Database Stats
- **Resources**: 3,000-4,000
- **Links**: 100,000-150,000
- **Database Size**: ~150-200MB
- **Query Speed**: <50ms for most queries

---

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask 3.0
- **Database**: SQLite
- **Crawler**: Selenium WebDriver
- **Search**: scikit-learn (TF-IDF)
- **Auth**: PyJWT
- **Language**: Python 3.8+

### Frontend
- **Framework**: React 18.2
- **Build Tool**: Vite 5.0
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Styling**: Custom CSS (CSS Variables)
- **Language**: JavaScript (JSX)

### Algorithms
- **Search**: TF-IDF (scikit-learn)
- **Ranking**: PageRank (custom implementation)
- **Crawling**: Breadth-First Search (BFS)
- **Recommendations**: Hybrid collaborative filtering

---

## 🔐 Security Considerations

### Current Implementation
- ✅ JWT authentication
- ✅ CORS configuration
- ✅ Input validation
- ✅ SQL injection prevention (parameterized queries)
- ⚠️ Passwords stored in plain text (development only)

### Production Recommendations
- 🔒 Use bcrypt for password hashing
- 🔒 Enable HTTPS only
- 🔒 Implement rate limiting
- 🔒 Add CSRF protection
- 🔒 Secure JWT secret
- 🔒 Input sanitization
- 🔒 Database access controls

---

## 🚢 Deployment

### Backend (Example: Heroku)

```bash
# Prepare
echo "web: gunicorn app:app" > backend/Procfile
pip freeze > backend/requirements.txt

# Deploy
heroku create ml-xplore-api
git subtree push --prefix backend heroku main
```

### Frontend (Example: Vercel)

```bash
cd frontend
npm run build
vercel --prod
```

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

---

## 🎓 Educational Value

This project demonstrates:

### Algorithms & Data Structures
- ✅ Breadth-First Search (BFS) for web crawling
- ✅ TF-IDF for information retrieval
- ✅ PageRank for graph-based ranking
- ✅ Hybrid recommendation systems
- ✅ Graph data structures

### Software Engineering
- ✅ Full-stack development (Flask + React)
- ✅ RESTful API design
- ✅ Database schema design
- ✅ Authentication & authorization
- ✅ Error handling & validation

### Machine Learning
- ✅ Text processing & NLP
- ✅ Feature extraction (TF-IDF)
- ✅ Similarity metrics
- ✅ Recommendation algorithms
- ✅ Web scraping at scale

### Best Practices
- ✅ Clean code architecture
- ✅ Modular design
- ✅ Documentation
- ✅ Version control
- ✅ Testing

Perfect for portfolios, learning, and job interviews!

---


## 🗺️ Roadmap

### Current Features (v1.0)
- ✅ Multi-source web crawling
- ✅ TF-IDF search
- ✅ PageRank ranking
- ✅ User authentication
- ✅ Personalized recommendations
- ✅ History tracking
- ✅ Admin dashboard

### Planned Features (v2.0)
- 🔄 Real-time crawling updates
- 🔄 Advanced filters (date, source, difficulty)
- 🔄 Bookmarking system
- 🔄 User collections
- 🔄 Social features (sharing, comments)
- 🔄 Email notifications
- 🔄 Mobile app
- 🔄 Dark/light mode toggle

### Future Enhancements
- 🔮 Neural embeddings (BERT, Sentence-BERT)
- 🔮 Semantic search
- 🔮 Collaborative filtering
- 🔮 Auto-categorization with ML
- 🔮 Duplicate detection
- 🔮 Multi-language support
- 🔮 GraphQL API
- 🔮 Elasticsearch integration

---

<div align="center">

## ⭐ Star this repo if you find it helpful!

</div>
