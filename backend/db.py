import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_PATH = os.getenv('DATABASE_PATH', '../database/database.db')
DATABASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), DATABASE_PATH))

def setup_database():
    """Initialize all database tables"""
    # Ensure the database directory exists
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Resources table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            title TEXT,
            description TEXT,
            summary TEXT,
            tags TEXT,
            last_crawled DATETIME DEFAULT CURRENT_TIMESTAMP,
            popularity_score FLOAT DEFAULT 0.0
        );
    """)
    print("✓ Table 'resources' created successfully.")
    
    # Links table for PageRank
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_url TEXT NOT NULL,
            destination_url TEXT NOT NULL,
            FOREIGN KEY (source_url) REFERENCES resources(url) ON DELETE CASCADE,
            FOREIGN KEY (destination_url) REFERENCES resources(url) ON DELETE CASCADE,
            UNIQUE (source_url, destination_url)
        );
    """)
    print("✓ Table 'links' created successfully.")
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            preferences TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print("✓ Table 'users' created successfully.")
    
    # User interactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_source_interaction (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            resource_url TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (resource_url) REFERENCES resources(url) ON DELETE CASCADE
        );
    """)
    print("✓ Table 'user_source_interaction' created successfully.")
    
    # Create indexes for better performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_resources_url ON resources(url);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_links_source ON links(source_url);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_links_dest ON links(destination_url);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_interactions ON user_source_interaction(user_id);")
    print("✓ Indexes created successfully.")
    
    conn.commit()
    conn.close()
    print(f"\n✓ Database initialized at: {DATABASE_PATH}")

if __name__ == "__main__":
    setup_database()