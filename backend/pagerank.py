import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_PATH = os.getenv('DATABASE_PATH', '../database/database.db')
DATABASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), DATABASE_PATH))

def fetch_links():
    """Fetch all links from the database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT source_url, destination_url FROM links")
    links = cursor.fetchall()
    conn.close()
    return links

def initialize_pagerank(links):
    """Initialize PageRank dictionary with equal values"""
    pages = set()
    for source, destination in links:
        pages.add(source)
        pages.add(destination)
    pagerank = {page: 1.0 for page in pages}
    return pagerank, pages

def calculate_pagerank(links, damping_factor=0.85, iterations=20):
    """Calculate PageRank scores for all pages"""
    print("Calculating PageRank scores...")
    print("=" * 60)
    
    pagerank, pages = initialize_pagerank(links)
    
    if not pages:
        print("No pages found to rank!")
        return {}
    
    print(f"Total pages: {len(pages)}")
    print(f"Total links: {len(links)}")
    print(f"Damping factor: {damping_factor}")
    print(f"Iterations: {iterations}")
    
    inbound_links = {page: [] for page in pages}
    outbound_links = {page: 0 for page in pages}
    
    for source, destination in links:
        inbound_links[destination].append(source)
        outbound_links[source] += 1
    
    for iteration in range(iterations):
        new_pagerank = {}
        for page in pages:
            rank_sum = 0
            for inbound_page in inbound_links[page]:
                if outbound_links[inbound_page] > 0:
                    rank_sum += pagerank[inbound_page] / outbound_links[inbound_page]
            new_pagerank[page] = (1 - damping_factor) + damping_factor * rank_sum
        pagerank = new_pagerank
        
        if (iteration + 1) % 5 == 0:
            print(f"  Iteration {iteration + 1}/{iterations} completed")
    
    return pagerank

def store_pagerank(pagerank):
    """Store PageRank scores in the database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    updated = 0
    for url, score in pagerank.items():
        cursor.execute("UPDATE resources SET popularity_score = ? WHERE url = ?", (score, url))
        updated += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n✓ Updated {updated} PageRank scores")

def main():
    """Main function to calculate and store PageRank"""
    links = fetch_links()
    
    if not links:
        print("No links found in database!")
        return
    
    pagerank = calculate_pagerank(links)
    store_pagerank(pagerank)
    
    print(f"\n{'=' * 60}")
    print("✓ PageRank calculation completed!")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()