from database import engine
from sqlalchemy import text

def update_schema():
    print("Starting schema migration...")
    with engine.connect() as conn:
        # 1. Add social_links column
        try:
            conn.execute(text("ALTER TABLE blog_authors ADD COLUMN IF NOT EXISTS social_links JSON;"))
            print("✅ Added column: social_links")
        except Exception as e:
            print(f"⚠️ Could not add social_links (might exist): {e}")

        # 2. Add books column
        try:
            conn.execute(text("ALTER TABLE blog_authors ADD COLUMN IF NOT EXISTS books JSON;"))
            print("✅ Added column: books")
        except Exception as e:
            print(f"⚠️ Could not add books (might exist): {e}")

        # 3. Add Store Product columns
        try:
            conn.execute(text("ALTER TABLE store_products ADD COLUMN IF NOT EXISTS version VARCHAR(50);"))
            conn.execute(text("ALTER TABLE store_products ADD COLUMN IF NOT EXISTS tags JSON;"))
            conn.execute(text("ALTER TABLE store_products ADD COLUMN IF NOT EXISTS preview_url VARCHAR(500);"))
            print("✅ Added columns: version, tags, preview_url to store_products")
        except Exception as e:
            print(f"⚠️ Could not add store columns: {e}")
            
        conn.commit()
        print("🎉 Database schema update complete.")

if __name__ == "__main__":
    update_schema()
