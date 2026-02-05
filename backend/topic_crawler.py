import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from collections import deque
import time
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_PATH = os.getenv('DATABASE_PATH', '../database/database.db')
DATABASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), DATABASE_PATH))

from mega_crawler import (
    assign_tags, store_resource, store_link, setup_driver,
    check_arxiv_page, check_medium_page, check_huggingface_page,
    check_paperswithcode_page, check_github_page
)

# -------------------- SPECIFIC TOPIC QUERIES --------------------

SPECIFIC_TOPICS = {
    "Multimodal LLMs": [
        ("ArXiv - Multimodal", "https://arxiv.org/search/?query=multimodal+language+model", check_arxiv_page),
        ("Medium - Multimodal AI", "https://medium.com/search?q=multimodal%20llm", check_medium_page),
        ("Papers with Code - Multimodal", "https://paperswithcode.com/task/multimodal-learning", check_paperswithcode_page),
        ("Hugging Face - Multimodal", "https://huggingface.co/models?pipeline_tag=image-to-text", check_huggingface_page),
    ],
    
    "Edge AI": [
        ("ArXiv - Edge AI", "https://arxiv.org/search/?query=edge+computing+ai", check_arxiv_page),
        ("Medium - Edge AI", "https://medium.com/search?q=edge%20ai", check_medium_page),
        ("Papers with Code - Edge", "https://paperswithcode.com/search?q=edge+ai", check_paperswithcode_page),
    ],
    
    "Imitation Learning": [
        ("ArXiv - Imitation Learning", "https://arxiv.org/search/?query=imitation+learning", check_arxiv_page),
        ("Medium - Imitation Learning", "https://medium.com/search?q=imitation%20learning", check_medium_page),
        ("Papers with Code - Imitation", "https://paperswithcode.com/task/imitation-learning", check_paperswithcode_page),
    ],
    
    "Few-Shot Learning": [
        ("ArXiv - Few-Shot", "https://arxiv.org/search/?query=few-shot+learning", check_arxiv_page),
        ("Medium - Few-Shot", "https://medium.com/search?q=few-shot%20learning", check_medium_page),
        ("Papers with Code - Few-Shot", "https://paperswithcode.com/task/few-shot-learning", check_paperswithcode_page),
    ],
    
    "Meta-Learning": [
        ("ArXiv - Meta-Learning", "https://arxiv.org/search/?query=meta+learning", check_arxiv_page),
        ("Medium - Meta-Learning", "https://medium.com/search?q=meta%20learning", check_medium_page),
    ],
    
    "Federated Learning": [
        ("ArXiv - Federated", "https://arxiv.org/search/?query=federated+learning", check_arxiv_page),
        ("Medium - Federated", "https://medium.com/search?q=federated%20learning", check_medium_page),
        ("Papers with Code - Federated", "https://paperswithcode.com/task/federated-learning", check_paperswithcode_page),
    ],
    
    "Self-Supervised Learning": [
        ("ArXiv - Self-Supervised", "https://arxiv.org/search/?query=self-supervised+learning", check_arxiv_page),
        ("Medium - Self-Supervised", "https://medium.com/search?q=self-supervised%20learning", check_medium_page),
    ],
    
    "Continual Learning": [
        ("ArXiv - Continual Learning", "https://arxiv.org/search/?query=continual+learning", check_arxiv_page),
        ("Medium - Continual Learning", "https://medium.com/search?q=continual%20learning", check_medium_page),
    ],
    
    "Neural Architecture Search": [
        ("ArXiv - NAS", "https://arxiv.org/search/?query=neural+architecture+search", check_arxiv_page),
        ("Papers with Code - NAS", "https://paperswithcode.com/task/neural-architecture-search", check_paperswithcode_page),
    ],
    
    "Graph Neural Networks": [
        ("ArXiv - GNN", "https://arxiv.org/search/?query=graph+neural+network", check_arxiv_page),
        ("Medium - GNN", "https://medium.com/search?q=graph%20neural%20network", check_medium_page),
        ("Papers with Code - GNN", "https://paperswithcode.com/methods/category/graph-neural-networks", check_paperswithcode_page),
    ],
    
    "Diffusion Models": [
        ("ArXiv - Diffusion", "https://arxiv.org/search/?query=diffusion+model", check_arxiv_page),
        ("Medium - Diffusion", "https://medium.com/search?q=diffusion%20models", check_medium_page),
        ("Hugging Face - Diffusion", "https://huggingface.co/models?pipeline_tag=text-to-image", check_huggingface_page),
    ],
    
    "Vision Transformers": [
        ("ArXiv - ViT", "https://arxiv.org/search/?query=vision+transformer", check_arxiv_page),
        ("Papers with Code - ViT", "https://paperswithcode.com/method/vision-transformer", check_paperswithcode_page),
    ],
    
    "RLHF": [
        ("ArXiv - RLHF", "https://arxiv.org/search/?query=reinforcement+learning+human+feedback", check_arxiv_page),
        ("Medium - RLHF", "https://medium.com/search?q=rlhf", check_medium_page),
    ],
    
    "Prompt Engineering": [
        ("ArXiv - Prompt Engineering", "https://arxiv.org/search/?query=prompt+engineering", check_arxiv_page),
        ("Medium - Prompt Engineering", "https://medium.com/search?q=prompt%20engineering", check_medium_page),
    ],
    
    "RAG (Retrieval Augmented Generation)": [
        ("ArXiv - RAG", "https://arxiv.org/search/?query=retrieval+augmented+generation", check_arxiv_page),
        ("Medium - RAG", "https://medium.com/search?q=retrieval%20augmented%20generation", check_medium_page),
    ],
}

# -------------------- CRAWL FUNCTION --------------------

def crawl_site(start_url, max_depth, check_function, driver, visited_links, max_pages=50):
    """Crawl with page limit"""
    queue = deque([(start_url, 1)])
    site_visited = set()
    pages_crawled = 0

    while queue and pages_crawled < max_pages:
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
            time.sleep(1)

            title = driver.title
            try:
                description = driver.find_element(
                    By.CSS_SELECTOR, 'meta[name="description"]'
                ).get_attribute('content')
            except:
                description = ''

            content = driver.find_element(By.TAG_NAME, 'body').text[:500]
            tags = assign_tags(content, url)

            store_resource(url, title, description, tags)
            pages_crawled += 1

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
            continue

    return pages_crawled

# -------------------- MAIN --------------------

def main():
    print("=" * 80)
    print(" " * 20 + "TOPIC-SPECIFIC ML CRAWLER")
    print(" " * 15 + "Covering Niche and Advanced ML Topics")
    print("=" * 80)
    print()
    
    print("Topics to cover:")
    for i, topic in enumerate(SPECIFIC_TOPICS.keys(), 1):
        print(f"  {i:2d}. {topic}")
    print()
    
    driver = setup_driver()
    visited_links = set()
    total_crawled = 0
    
    topic_count = 0
    
    for topic_name, sources in SPECIFIC_TOPICS.items():
        topic_count += 1
        print(f"\n{'=' * 80}")
        print(f"[{topic_count}/{len(SPECIFIC_TOPICS)}] TOPIC: {topic_name}")
        print(f"{'=' * 80}")
        
        topic_crawled = 0
        
        for source_name, url, check_func in sources:
            print(f"\n  Crawling: {source_name}")
            print(f"  URL: {url[:70]}...")
            
            try:
                crawled = crawl_site(url, 3, check_func, driver, visited_links, max_pages=30)
                topic_crawled += crawled
                total_crawled += crawled
                print(f"  ✓ Crawled {crawled} pages")
            except Exception as e:
                print(f"  ✗ Error: {str(e)[:60]}")
        
        print(f"\n  Topic '{topic_name}' total: {topic_crawled} resources")
    
    driver.quit()
    
    # Get stats
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM links")
    total_links = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM resources")
    total_resources = cursor.fetchone()[0]
    conn.close()
    
    print(f"\n{'=' * 80}")
    print(f"✓ TOPIC-SPECIFIC CRAWLING COMPLETED!")
    print(f"{'=' * 80}")
    print(f"Topics covered: {len(SPECIFIC_TOPICS)}")
    print(f"New resources: {total_crawled}")
    print(f"Total resources in DB: {total_resources}")
    print(f"Total links in DB: {total_links}")
    print(f"{'=' * 80}")
    print("\nNow your search should find results for:")
    for topic in SPECIFIC_TOPICS.keys():
        print(f"  ✓ {topic}")

if __name__ == "__main__":
    main()