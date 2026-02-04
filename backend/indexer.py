import sqlite3
import time
import os
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from sklearn.feature_extraction.text import TfidfVectorizer

load_dotenv()

# -------------------- DATABASE --------------------

DATABASE_PATH = os.getenv('DATABASE_PATH', '../data/database.db')
DATABASE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), DATABASE_PATH)
)

# -------------------- DB FETCH --------------------

def fetch_pages_without_summary():
    """Fetch all pages that need summaries"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT url, description, title
        FROM resources
        WHERE summary IS NULL OR summary = ''
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

# -------------------- SELENIUM --------------------

def setup_driver():
    """Set up Selenium WebDriver (auto-managed ChromeDriver)"""
    chrome_options = Options()
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    return webdriver.Chrome(options=chrome_options)

def fetch_page_body(url, driver):
    """Fetch the body text of a webpage"""
    try:
        driver.get(url)
        time.sleep(3)
        body = driver.find_element(By.TAG_NAME, 'body').text
        return body
    except Exception as e:
        print(f"Error fetching body for {url}: {e}")
        return ""

# -------------------- SUMMARY GENERATION --------------------

def generate_summaries():
    print("Starting summary generation...")
    print("=" * 60)

    pages = fetch_pages_without_summary()
    if not pages:
        print("✓ All pages already have summaries!")
        return

    print(f"Found {len(pages)} pages to process")

    driver = setup_driver()
    vectorizer = TfidfVectorizer(
        max_features=30,
        stop_words='english'
    )

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    processed = 0

    try:
        for idx, (url, description, title) in enumerate(pages, start=1):
            try:
                print(f"[{idx}/{len(pages)}] Processing: {url}")

                page_body = fetch_page_body(url, driver)
                
                # Include title for better context (title is very important for matching)
                full_content = f"{title or ''} {description or ''} {page_body}"

                if not full_content.strip():
                    cursor.execute(
                        "UPDATE resources SET summary = ? WHERE url = ?",
                        ('', url)
                    )
                    conn.commit()
                    continue

                tfidf_matrix = vectorizer.fit_transform([full_content])
                terms = vectorizer.get_feature_names_out()

                sorted_terms = [
                    terms[i] for i in tfidf_matrix[0].indices
                ]

                # Create a richer summary with more terms
                summary = " ".join(sorted_terms[:25])

                cursor.execute(
                    "UPDATE resources SET summary = ? WHERE url = ?",
                    (summary, url)
                )
                conn.commit()

                processed += 1

            except Exception as e:
                print(f"Error processing {url}: {e}")
                cursor.execute(
                    "UPDATE resources SET summary = ? WHERE url = ?",
                    ('', url)
                )
                conn.commit()

    finally:
        conn.close()
        driver.quit()

    print(f"\n{'=' * 60}")
    print(f"✓ Summary generation completed! Processed {processed} pages")
    print(f"{'=' * 60}")

# -------------------- ENTRY POINT --------------------

if __name__ == "__main__":
    generate_summaries()
