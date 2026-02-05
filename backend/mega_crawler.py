import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from collections import deque
import time
import os
import re
from dotenv import load_dotenv
import random

load_dotenv()

# -------------------- DATABASE --------------------

DATABASE_PATH = os.getenv('DATABASE_PATH', '../database/database.db')
DATABASE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), DATABASE_PATH)
)

# -------------------- TAG KEYWORDS --------------------

category_keywords = {
    "dataset": ["dataset", "data collection", "data source", "training data", "benchmark"],
    "model": ["model", "algorithm", "neural network", "training", "inference", "architecture"],
    "article": ["article", "guide", "tutorial", "how-to", "introduction", "overview"],
    "research paper": ["research paper", "study", "journal", "publication", "arxiv", "conference", "proceedings", "ieee"],
    "documentation": ["documentation", "api", "reference", "docs"],
    "code": ["code", "implementation", "github", "repository", "example"]
}

# -------------------- HELPERS --------------------

def assign_tags(content, url=""):
    """Determine tags based on content and URL"""
    tags = []
    content_lower = content.lower()
    url_lower = url.lower()
    
    # Check URL patterns first for more accurate tagging
    if 'kaggle.com/datasets' in url_lower:
        tags.append('dataset')
    elif 'kaggle.com/models' in url_lower:
        tags.append('model')
    elif 'arxiv.org' in url_lower or 'ieeexplore.ieee.org' in url_lower:
        tags.append('research paper')
    elif 'github.com' in url_lower:
        tags.append('code')
    
    # Then check content
    for category, keywords in category_keywords.items():
        if category not in tags:
            if any(re.search(r'\b' + keyword + r'\b', content_lower) for keyword in keywords):
                tags.append(category)
    
    return ", ".join(tags) if tags else "general"

def store_resource(url, title, description, tags):
    """Insert a new resource into the database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO resources (url, title, description, tags)
            VALUES (?, ?, ?, ?)
        """, (url, title, description, tags))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error storing resource: {e}")
    finally:
        conn.close()

def store_link(source_url, destination_url):
    """Insert a link between two pages"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO links (source_url, destination_url)
            VALUES (?, ?)
        """, (source_url, destination_url))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error storing link: {e}")
    finally:
        conn.close()

# -------------------- SITE FILTERS --------------------

def check_kaggle_page(url):
    if any(symbol in url for symbol in ['#', '%']):
        return None
    if url.endswith(('/discussions', '/code', '/suggestions', '/competitions')):
        return None
    if '/discussion' in url:
        return None
    if 'kaggle.com/datasets' in url:
        return 'dataset'
    elif 'kaggle.com/models' in url:
        return 'model'
    elif 'kaggle.com/learn' in url:
        return 'article'
    return None

def check_medium_page(url):
    """Check Medium articles - very permissive for more content"""
    if 'medium.com' in url:
        if any(x in url for x in ['/plans', '/membership', '/about', '/jobs', '/newsletter']):
            return None
        # Very permissive - accept most Medium URLs
        return 'article'
    return None

def check_towardsdatascience_page(url):
    """Check Towards Data Science"""
    if 'towardsdatascience.com' in url:
        if any(x in url for x in ['#', '/plans', '/membership']):
            return None
        return 'article'
    return None

def check_arxiv_page(url):
    """Check ArXiv papers - very important for research"""
    if 'arxiv.org' in url and '/abs/' in url:
        return 'research paper'
    return None

def check_huggingface_page(url):
    """Check Hugging Face - models, datasets, papers"""
    if 'huggingface.co' in url:
        if any(x in url for x in ['#', '?page=']):
            return None
        if '/datasets/' in url:
            return 'dataset'
        elif '/models/' in url or '/spaces/' in url:
            return 'model'
        elif '/papers/' in url:
            return 'research paper'
        elif '/docs/' in url:
            return 'documentation'
    return None

def check_paperswithcode_page(url):
    """Check Papers with Code"""
    if 'paperswithcode.com' in url:
        if any(x in url for x in ['#']):
            return None
        if '/paper/' in url or '/method/' in url or '/task/' in url:
            return 'research paper'
        elif '/dataset/' in url:
            return 'dataset'
    return None

def check_github_page(url):
    """Check GitHub repositories - important for code"""
    if 'github.com' in url:
        if any(x in url for x in ['#', '/issues/', '/pull/', '/actions/', '/wiki/', '/settings/']):
            return None
        # Accept repos with ML keywords
        ml_keywords = ['machine-learning', 'deep-learning', 'neural', 'tensorflow', 'pytorch', 
                       'ai', 'ml', 'llm', 'transformer', 'vision', 'nlp']
        if any(kw in url.lower() for kw in ml_keywords):
            return 'code'
    return None

def check_distill_page(url):
    """Check Distill.pub - high quality ML articles"""
    if 'distill.pub' in url:
        return 'article'
    return None

def check_openai_page(url):
    """Check OpenAI blog and research"""
    if 'openai.com' in url:
        if '/research/' in url or '/blog/' in url:
            return 'article'
    return None

def check_deepmind_page(url):
    """Check DeepMind blog and research"""
    if 'deepmind.com' in url or 'deepmind.google' in url:
        if any(x in url for x in ['/blog/', '/research/', '/publications/']):
            return 'article'
    return None

def check_ai_googleblog_page(url):
    """Check Google AI Blog"""
    if 'ai.googleblog.com' in url or 'blog.research.google' in url:
        return 'article'
    return None

def check_machinelearningmastery_page(url):
    """Check ML Mastery"""
    if 'machinelearningmastery.com' in url:
        if any(x in url for x in ['#', '/blog/', '/start-here/', '/about/']):
            return None
        return 'article'
    return None

def check_analyticsvidhya_page(url):
    """Check Analytics Vidhya"""
    if 'analyticsvidhya.com' in url:
        if '/blog/' in url or '/learn/' in url:
            return 'article'
    return None

def check_kdnuggets_page(url):
    """Check KDnuggets"""
    if 'kdnuggets.com' in url:
        if any(x in url for x in ['#', '/tag/', '/author/']):
            return None
        return 'article'
    return None

# -------------------- SELENIUM SETUP --------------------

def setup_driver():
    """Set up Selenium WebDriver with optimizations"""
    chrome_options = Options()
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-images")  # Faster loading
    chrome_options.add_argument("--disable-javascript")  # Even faster
    chrome_options.page_load_strategy = 'eager'  # Don't wait for full load
    
    return webdriver.Chrome(options=chrome_options)

# -------------------- CRAWLER --------------------

def crawl_site(start_url, max_depth, check_function, driver, visited_links, max_pages=None):
    """Crawl with optional page limit"""
    queue = deque([(start_url, 1)])
    site_visited = set()
    pages_crawled = 0

    while queue:
        if max_pages and pages_crawled >= max_pages:
            break
            
        url, depth = queue.popleft()

        if depth > max_depth or url in visited_links or url in site_visited:
            continue

        result = check_function(url)
        if result is None:
            continue

        site_visited.add(url)
        visited_links.add(url)

        try:
            driver.get(url)
            time.sleep(1)  # Reduced sleep for faster crawling

            title = driver.title
            try:
                description = driver.find_element(
                    By.CSS_SELECTOR, 'meta[name="description"]'
                ).get_attribute('content')
            except:
                description = ''

            content = driver.find_element(By.TAG_NAME, 'body').text[:500]  # Only first 500 chars
            tags = assign_tags(content, url)

            store_resource(url, title, description, tags)
            pages_crawled += 1

            if pages_crawled % 10 == 0:
                print(f"  [{pages_crawled}] {url[:80]}...")

            # Get links
            links = driver.find_elements(By.TAG_NAME, 'a')
            for link in links:
                try:
                    href = link.get_attribute('href')
                    if href and href.startswith('http') and href not in visited_links:
                        store_link(url, href)
                        if check_function(href):
                            queue.append((href, depth + 1))
                except:
                    continue

        except Exception as e:
            print(f"  Error: {url[:60]}... - {str(e)[:40]}")
            continue

    return pages_crawled

# -------------------- MAIN --------------------

def main():
    print("=" * 80)
    print(" " * 20 + "MEGA ML RESOURCE CRAWLER")
    print(" " * 15 + "Target: 100,000+ Links from 1000+ Resources")
    print("=" * 80)
    print()

    driver = setup_driver()
    visited_links = set()
    total_crawled = 0

    # MASSIVE crawl targets - prioritize research papers and diverse sources
    crawl_targets = [
        # ========== RESEARCH PAPERS (TOP PRIORITY) ==========
        ("ArXiv - Machine Learning", "https://arxiv.org/list/cs.LG/recent", 4, check_arxiv_page, 300),
        ("ArXiv - AI", "https://arxiv.org/list/cs.AI/recent", 4, check_arxiv_page, 300),
        ("ArXiv - Computer Vision", "https://arxiv.org/list/cs.CV/recent", 4, check_arxiv_page, 200),
        ("ArXiv - NLP", "https://arxiv.org/list/cs.CL/recent", 4, check_arxiv_page, 200),
        ("ArXiv - Robotics", "https://arxiv.org/list/cs.RO/recent", 3, check_arxiv_page, 100),
        
        # Papers with Code
        ("Papers with Code - Browse", "https://paperswithcode.com/methods", 4, check_paperswithcode_page, 200),
        ("Papers with Code - Datasets", "https://paperswithcode.com/datasets", 4, check_paperswithcode_page, 150),
        ("Papers with Code - SOTA", "https://paperswithcode.com/sota", 4, check_paperswithcode_page, 150),
        
        # ========== MODELS & DATASETS ==========
        ("Hugging Face - Models", "https://huggingface.co/models", 3, check_huggingface_page, 300),
        ("Hugging Face - Datasets", "https://huggingface.co/datasets", 3, check_huggingface_page, 200),
        ("Hugging Face - Papers", "https://huggingface.co/papers", 3, check_huggingface_page, 150),
        
        ("Kaggle - Datasets", "https://www.kaggle.com/datasets", 3, check_kaggle_page, 200),
        ("Kaggle - Models", "https://www.kaggle.com/models", 3, check_kaggle_page, 150),
        
        # ========== HIGH-QUALITY ARTICLES ==========
        ("Distill.pub", "https://distill.pub/", 3, check_distill_page, 50),
        
        ("Medium - Machine Learning", "https://medium.com/tag/machine-learning", 4, check_medium_page, 300),
        ("Medium - Deep Learning", "https://medium.com/tag/deep-learning", 4, check_medium_page, 300),
        ("Medium - AI", "https://medium.com/tag/artificial-intelligence", 4, check_medium_page, 200),
        ("Medium - NLP", "https://medium.com/tag/nlp", 3, check_medium_page, 150),
        ("Medium - Computer Vision", "https://medium.com/tag/computer-vision", 3, check_medium_page, 150),
        ("Medium - LLMs", "https://medium.com/tag/large-language-models", 3, check_medium_page, 100),
        
        ("Towards Data Science - ML", "https://towardsdatascience.com/tagged/machine-learning", 4, check_towardsdatascience_page, 300),
        ("Towards Data Science - DL", "https://towardsdatascience.com/tagged/deep-learning", 4, check_towardsdatascience_page, 300),
        ("Towards Data Science - AI", "https://towardsdatascience.com/tagged/artificial-intelligence", 4, check_towardsdatascience_page, 200),
        
        ("ML Mastery - Deep Learning", "https://machinelearningmastery.com/category/deep-learning/", 3, check_machinelearningmastery_page, 150),
        ("ML Mastery - NLP", "https://machinelearningmastery.com/category/natural-language-processing/", 3, check_machinelearningmastery_page, 100),
        
        ("Analytics Vidhya", "https://www.analyticsvidhya.com/blog/", 3, check_analyticsvidhya_page, 200),
        ("KDnuggets", "https://www.kdnuggets.com/", 3, check_kdnuggets_page, 150),
        
        # ========== COMPANY RESEARCH BLOGS ==========
        ("OpenAI Research", "https://openai.com/research/", 3, check_openai_page, 100),
        ("Google AI Blog", "https://blog.research.google/", 3, check_ai_googleblog_page, 150),
        ("DeepMind Research", "https://deepmind.google/research/", 3, check_deepmind_page, 100),
        
        # ========== CODE REPOSITORIES ==========
        ("GitHub - PyTorch", "https://github.com/pytorch/pytorch", 2, check_github_page, 50),
        ("GitHub - TensorFlow", "https://github.com/tensorflow/tensorflow", 2, check_github_page, 50),
        ("GitHub - Transformers", "https://github.com/huggingface/transformers", 2, check_github_page, 50),
    ]

    print(f"Total crawl targets: {len(crawl_targets)}")
    print(f"Estimated resources to crawl: {sum(t[4] for t in crawl_targets)}")
    print()
    
    try:
        for i, (name, start_url, max_depth, check_func, max_pages) in enumerate(crawl_targets, 1):
            print(f"\n[{i}/{len(crawl_targets)}] {name}")
            print(f"URL: {start_url}")
            print(f"Max pages: {max_pages}, Max depth: {max_depth}")
            print("-" * 80)
            
            crawled = crawl_site(
                start_url, max_depth, check_func, driver, visited_links, max_pages
            )
            total_crawled += crawled
            
            print(f"✓ Crawled {crawled} pages from {name}")
            print(f"Total so far: {total_crawled} resources, {len(visited_links)} unique URLs")
            
            # Small delay between sources
            time.sleep(2)
            
    finally:
        driver.quit()

    # Get final link count
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM links")
    total_links = cursor.fetchone()[0]
    conn.close()

    print(f"\n{'=' * 80}")
    print(f"✓ CRAWLING COMPLETED!")
    print(f"{'=' * 80}")
    print(f"Total Resources: {total_crawled}")
    print(f"Total Unique URLs: {len(visited_links)}")
    print(f"Total Links: {total_links}")
    print(f"{'=' * 80}")
    print("\nNext steps:")
    print("1. Run: python indexer.py  (to generate summaries)")
    print("2. Run: python pagerank.py  (to calculate rankings)")
    print("3. Run: python check_db.py  (to verify)")

if __name__ == "__main__":
    main()