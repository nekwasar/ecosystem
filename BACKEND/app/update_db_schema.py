from database import engine
from sqlalchemy import text

def update_schema():
    print("Starting schema migration...")
    with engine.connect() as conn:
        # 1. Add social_links column
        try:
            # Note: IF NOT EXISTS syntax depends on Postgres version, but usually safe to wrap in try/except 
            # or check information_schema. But for simple dev usage, we'll try raw ALTER.
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
            
        conn.commit()
        print("🎉 Database schema update complete.")

if __name__ == "__main__":
    update_schema()
