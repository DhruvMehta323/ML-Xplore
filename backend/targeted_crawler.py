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

DATABASE_PATH = os.getenv('DATABASE_PATH', '../database/database.db')
DATABASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), DATABASE_PATH))

from crawler import (
    assign_tags, store_resource, store_link, setup_driver,
    check_kaggle_page, check_medium_page, check_towardsdatascience_page,
    check_arxiv_page, check_ieee_page, check_paperswithcode_page,
    check_machinelearningmastery_page
)

def crawl_specific_target(start_url, max_depth, check_function, driver, visited_links, max_pages=50):
    """Crawl with a page limit for targeted collection"""
    queue = deque([(start_url, 1)])
    site_visited = set()
    pages_crawled = 0

    while queue and pages_crawled < max_pages:
        url, depth = queue.popleft()

        if depth > max_depth or url in visited_links or url in site_visited:
            continue

        print(f"[{pages_crawled + 1}/{max_pages}] [Depth {depth}] Crawling: {url}")

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
            tags = assign_tags(content, url)

            store_resource(url, title, description, tags)
            pages_crawled += 1

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

    return pages_crawled

def main():
    print("=" * 70)
    print("  TARGETED ML RESOURCE CRAWLER")
    print("  Collect specific types of resources")
    print("=" * 70)
    print()
    print("Select resource type to crawl:")
    print("1. Kaggle Datasets (50 datasets)")
    print("2. Research Papers - ArXiv (50 papers)")
    print("3. Medium Articles (100 articles)")
    print("4. Towards Data Science (100 articles)")
    print("5. Machine Learning Mastery (50 articles)")
    print("6. Papers with Code (50 papers)")
    print("7. All of the above")
    print()
    
    choice = input("Enter choice (1-7): ").strip()
    
    driver = setup_driver()
    visited_links = set()
    total_crawled = 0

    targets = {
        "1": [("https://www.kaggle.com/datasets", 3, check_kaggle_page, 50, "Kaggle Datasets")],
        "2": [
            ("https://arxiv.org/list/cs.LG/recent", 2, check_arxiv_page, 25, "ArXiv ML"),
            ("https://arxiv.org/list/cs.AI/recent", 2, check_arxiv_page, 25, "ArXiv AI"),
        ],
        "3": [
            ("https://medium.com/tag/machine-learning/latest", 3, check_medium_page, 50, "Medium ML"),
            ("https://medium.com/tag/deep-learning/latest", 3, check_medium_page, 50, "Medium DL"),
        ],
        "4": [
            ("https://towardsdatascience.com/tagged/machine-learning", 3, check_towardsdatascience_page, 50, "TDS ML"),
            ("https://towardsdatascience.com/tagged/deep-learning", 3, check_towardsdatascience_page, 50, "TDS DL"),
        ],
        "5": [
            ("https://machinelearningmastery.com/category/deep-learning/", 3, check_machinelearningmastery_page, 25, "MLM DL"),
            ("https://machinelearningmastery.com/category/machine-learning/", 3, check_machinelearningmastery_page, 25, "MLM ML"),
        ],
        "6": [
            ("https://paperswithcode.com/methods/category/convolutional-neural-networks", 2, check_paperswithcode_page, 25, "PWC CNN"),
            ("https://paperswithcode.com/methods/category/transformers", 2, check_paperswithcode_page, 25, "PWC Trans"),
        ],
    }

    if choice == "7":
        # Crawl everything
        selected_targets = []
        for key in ["1", "2", "3", "4", "5", "6"]:
            selected_targets.extend(targets[key])
    elif choice in targets:
        selected_targets = targets[choice]
    else:
        print("Invalid choice!")
        driver.quit()
        return

    try:
        for start_url, max_depth, check_func, max_pages, name in selected_targets:
            print(f"\n{'=' * 70}")
            print(f"Crawling: {name}")
            print(f"URL: {start_url}")
            print(f"Max Pages: {max_pages}")
            print(f"{'=' * 70}\n")
            
            crawled = crawl_specific_target(
                start_url, max_depth, check_func, driver, visited_links, max_pages
            )
            total_crawled += crawled
            
            print(f"\n✓ Crawled {crawled} pages from {name}")
    finally:
        driver.quit()

    print(f"\n{'=' * 70}")
    print(f"✓ TOTAL CRAWLED: {total_crawled} pages")
    print(f"✓ Total unique URLs: {len(visited_links)}")
    print(f"{'=' * 70}")
    print("\nNext steps:")
    print("1. Run: python indexer.py  (to generate summaries)")
    print("2. Run: python pagerank.py  (to calculate rankings)")

if __name__ == "__main__":
    main()