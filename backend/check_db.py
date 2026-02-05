#!/usr/bin/env python3
"""
Database Diagnostic Tool
Check the status of your ML Resource database
"""

import sqlite3
import os
from dotenv import load_dotenv
from collections import Counter

load_dotenv()

DATABASE_PATH = os.getenv('DATABASE_PATH', '../database/database.db')
DATABASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), DATABASE_PATH))

def main():
    print("=" * 70)
    print("  ML RESOURCE DATABASE DIAGNOSTICS")
    print("=" * 70)
    print()

    if not os.path.exists(DATABASE_PATH):
        print(f"❌ Database not found at: {DATABASE_PATH}")
        print("   Run: python db.py to create it")
        return

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Total resources
    cursor.execute("SELECT COUNT(*) FROM resources")
    total_resources = cursor.fetchone()[0]
    print(f"📊 Total Resources: {total_resources}")

    # Resources with summaries
    cursor.execute("SELECT COUNT(*) FROM resources WHERE summary IS NOT NULL AND summary != ''")
    with_summaries = cursor.fetchone()[0]
    print(f"📝 With Summaries: {with_summaries} ({with_summaries/max(total_resources, 1)*100:.1f}%)")

    # Total links
    cursor.execute("SELECT COUNT(*) FROM links")
    total_links = cursor.fetchone()[0]
    print(f"🔗 Total Links: {total_links}")

    # Resources with PageRank > 0
    cursor.execute("SELECT COUNT(*) FROM resources WHERE popularity_score > 0")
    with_pagerank = cursor.fetchone()[0]
    print(f"⭐ With PageRank: {with_pagerank} ({with_pagerank/max(total_resources, 1)*100:.1f}%)")

    print()
    print("-" * 70)
    print("TAG DISTRIBUTION")
    print("-" * 70)

    # Tag distribution
    cursor.execute("SELECT tags FROM resources WHERE tags IS NOT NULL AND tags != ''")
    all_tags = []
    for row in cursor.fetchall():
        tags = row[0].split(',')
        all_tags.extend([tag.strip() for tag in tags if tag.strip()])

    tag_counts = Counter(all_tags)
    
    if tag_counts:
        for tag, count in tag_counts.most_common():
            bar = "█" * min(50, count)
            print(f"{tag:20} {count:5} {bar}")
    else:
        print("No tags found!")

    print()
    print("-" * 70)
    print("SOURCE DISTRIBUTION")
    print("-" * 70)

    # Source distribution
    cursor.execute("SELECT url FROM resources")
    sources = Counter()
    for row in cursor.fetchall():
        url = row[0]
        if 'geeksforgeeks.org' in url:
            sources['GeeksforGeeks'] += 1
        elif 'kaggle.com' in url:
            sources['Kaggle'] += 1
        elif 'medium.com' in url:
            sources['Medium'] += 1
        elif 'towardsdatascience.com' in url:
            sources['Towards Data Science'] += 1
        elif 'machinelearningmastery.com' in url:
            sources['ML Mastery'] += 1
        elif 'arxiv.org' in url:
            sources['ArXiv'] += 1
        elif 'ieeexplore.ieee.org' in url:
            sources['IEEE'] += 1
        elif 'paperswithcode.com' in url:
            sources['Papers with Code'] += 1
        else:
            sources['Other'] += 1

    if sources:
        max_count = max(sources.values())
        for source, count in sources.most_common():
            bar = "█" * int(50 * count / max_count)
            pct = count / total_resources * 100
            print(f"{source:25} {count:5} ({pct:5.1f}%) {bar}")
    else:
        print("No sources found!")

    print()
    print("-" * 70)
    print("SAMPLE RESOURCES BY TAG")
    print("-" * 70)

    for tag in ['dataset', 'model', 'article', 'research paper']:
        cursor.execute("""
            SELECT title, url 
            FROM resources 
            WHERE tags LIKE ? 
            LIMIT 3
        """, (f'%{tag}%',))
        
        results = cursor.fetchall()
        if results:
            print(f"\n{tag.upper()}:")
            for title, url in results:
                print(f"  • {title[:60]}...")
                print(f"    {url[:70]}...")
        else:
            print(f"\n{tag.upper()}: ❌ No resources found!")

    print()
    print("-" * 70)
    print("RECOMMENDATIONS")
    print("-" * 70)

    if total_resources == 0:
        print("❌ No resources in database!")
        print("   Run: python crawler.py or python targeted_crawler.py")
    elif with_summaries < total_resources:
        print("⚠️  Some resources missing summaries!")
        print(f"   {total_resources - with_summaries} resources need summaries")
        print("   Run: python indexer.py")
    elif with_pagerank < total_resources:
        print("⚠️  Some resources missing PageRank scores!")
        print("   Run: python pagerank.py")
    else:
        print("✅ Database looks good!")
        print("   All resources have summaries and PageRank scores")

    # Check for tag diversity
    print()
    if not tag_counts.get('dataset', 0):
        print("⚠️  No datasets found! Run targeted_crawler.py option 1")
    if not tag_counts.get('research paper', 0):
        print("⚠️  No research papers found! Run targeted_crawler.py option 2")

    # Check for source diversity
    gfg_ratio = sources.get('GeeksforGeeks', 0) / max(total_resources, 1)
    if gfg_ratio > 0.7:
        print(f"⚠️  Too much GeeksforGeeks content ({gfg_ratio*100:.0f}%)")
        print("   Run targeted_crawler.py to add diverse sources")

    conn.close()

    print()
    print("=" * 70)

if __name__ == "__main__":
    main()