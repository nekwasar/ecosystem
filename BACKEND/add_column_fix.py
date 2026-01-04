import sys
import os
from sqlalchemy import text

# Add current dir to path so we can import app
sys.path.append(os.path.join(os.getcwd()))

try:
    from app.database import engine
except ImportError:
    # Try appending 'app' parent
    sys.path.append(os.path.join(os.getcwd(), 'app'))
    from app.database import engine

def migrate():
    with engine.connect() as conn:
        try:
            print("Attempting to add segment_id column to newsletter_campaigns...")
            # PostgreSQL syntax
            conn.execute(text("ALTER TABLE newsletter_campaigns ADD COLUMN segment_id INTEGER REFERENCES newsletter_segments(id)"))
            conn.commit()
            print("Column added successfully.")
        except Exception as e:
            print(f"Migration result/error: {e}")

if __name__ == "__main__":
    migrate()
