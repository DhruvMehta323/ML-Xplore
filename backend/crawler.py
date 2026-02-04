import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from collections import deque
import time
import os
import re
from dotenv import load_dotenv

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
    
    # Then check content
    for category, keywords in category_keywords.items():
        if category not in tags:  # Avoid duplicates
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
    if any(symbol in url for symbol in ['#', '?', '%']):
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
    elif 'kaggle.com' in url:
        return 'home'
    return None

def check_geeksforgeeks_page(url):
    if '?' in url or '#' in url:
        return None
    if 'geeksforgeeks.org' in url and not any(x in url for x in ['/jobs/', '/courses/', '/newsletter', '/write/']):
        return 'article'
    return None

def check_medium_page(url):
    """Check Medium articles - more permissive"""
    if 'medium.com' in url:
        # Exclude certain sections
        if any(x in url for x in ['?', '#', '/tag/', '/topics/', '/plans', '/membership', '/about']):
            return None
        # Accept both user articles and publication articles
        if url.count('/') >= 3:  # More permissive
            return 'article'
    return None

def check_towardsdatascience_page(url):
    """Check Towards Data Science articles"""
    if 'towardsdatascience.com' in url:
        if any(x in url for x in ['?', '#', '/tagged/', '/plans']):
            return None
        if url.count('/') >= 3:
            return 'article'
    return None

def check_arxiv_page(url):
    """Check ArXiv papers"""
    if 'arxiv.org/abs/' in url:
        return 'research paper'
    return None

def check_ieee_page(url):
    """Check IEEE papers"""
    if 'ieeexplore.ieee.org/document/' in url:
        return 'research paper'
    return None

def check_paperswithcode_page(url):
    """Check Papers with Code"""
    if 'paperswithcode.com' in url:
        if any(x in url for x in ['?', '#']):
            return None
        if '/paper/' in url or '/dataset/' in url or '/method/' in url:
            return 'research paper'
    return None

def check_machinelearningmastery_page(url):
    """Check Machine Learning Mastery blog"""
    if 'machinelearningmastery.com' in url:
        if any(x in url for x in ['?', '#', '/blog/', '/start-here/', '/about/']):
            return None
        if url.count('/') >= 3:
            return 'article'
    return None

# -------------------- SELENIUM SETUP --------------------

def setup_driver():
    """Set up Selenium WebDriver (auto-managed ChromeDriver)"""
    chrome_options = Options()
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")

    return webdriver.Chrome(options=chrome_options)

# -------------------- CRAWLER --------------------

def crawl_site(start_url, max_depth, check_function, driver, visited_links):
    queue = deque([(start_url, 1)])
    site_visited = set()

    while queue:
        url, depth = queue.popleft()

        if depth > max_depth or url in visited_links or url in site_visited:
            continue

        print(f"[Depth {depth}] Crawling: {url}")

        if check_function(url) is None:
            continue

        site_visited.add(url)
        visited_links.add(url)

        try:
            driver.get(url)
            time.sleep(3)

            title = driver.title

            try:
                description = driver.find_element(
                    By.CSS_SELECTOR, 'meta[name="description"]'
                ).get_attribute('content')
            except:
                description = ''

            content = driver.find_element(By.TAG_NAME, 'body').text
            tags = assign_tags(content)

            store_resource(url, title, description, tags)

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
            print(f"Error crawling {url}: {e}")
            continue

# -------------------- MAIN --------------------

def main():
    print("Starting ML Resource Crawler...")
    print("=" * 60)

    driver = setup_driver()
    visited_links = set()

    crawl_targets = [
        # GeeksforGeeks
        ("https://www.geeksforgeeks.org/machine-learning/", 2, check_geeksforgeeks_page),
        
        # Kaggle
        ("https://www.kaggle.com/datasets", 2, check_kaggle_page),
        ("https://www.kaggle.com/models", 2, check_kaggle_page),
        
        # Medium & Towards Data Science
        ("https://medium.com/tag/machine-learning/latest", 3, check_medium_page),
        ("https://towardsdatascience.com/tagged/machine-learning", 3, check_towardsdatascience_page),
        ("https://towardsdatascience.com/tagged/deep-learning", 2, check_towardsdatascience_page),
        
        # Machine Learning Mastery
        ("https://machinelearningmastery.com/category/deep-learning/", 2, check_machinelearningmastery_page),
        
        # ArXiv (research papers)
        ("https://arxiv.org/list/cs.LG/recent", 2, check_arxiv_page),
        ("https://arxiv.org/list/cs.AI/recent", 2, check_arxiv_page),
        
        # Papers with Code
        ("https://paperswithcode.com/methods/category/convolutional-neural-networks", 2, check_paperswithcode_page),
    ]

    try:
        for start_url, max_depth, check_func in crawl_targets:
            print(f"\n{'=' * 60}")
            print(f"Crawling: {start_url}")
            print(f"Max Depth: {max_depth}")
            print(f"{'=' * 60}\n")
            crawl_site(start_url, max_depth, check_func, driver, visited_links)
    finally:
        driver.quit()

    print(f"\n{'=' * 60}")
    print(f"✓ Crawling completed! Total pages: {len(visited_links)}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
