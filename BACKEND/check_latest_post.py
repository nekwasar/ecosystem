import sys
import os
from sqlalchemy import create_engine, text
from datetime import datetime, timezone

# Add the 'app' directory to sys.path
sys.path.append(os.path.join(os.getcwd(), 'app'))

# Use raw connection to avoid ORM model conflict headaches in this inspection script
from app.core.config import settings
DATA_URL = settings.DATABASE_URL

engine = create_engine(DATA_URL)
print(f"SERVER TIME (UTC): {datetime.now(timezone.utc)}")

with engine.connect() as connection:
    result = connection.execute(text("SELECT id, title, slug, published_at FROM blog_posts ORDER BY id DESC LIMIT 1"))
    row = result.fetchone()
    
    if row:
        print(f"\n--- LATEST POST ---")
        print(f"ID: {row.id}")
        print(f"TITLE: {row.title}")
        print(f"SLUG: {row.slug}")
        # Note: published_at from DB might be naive or aware depending on driver
        published_at = row.published_at
        print(f"PUBLISHED_AT (DB): {published_at}")
        
        if published_at:
            if published_at.tzinfo is None:
                published_at = published_at.replace(tzinfo=timezone.utc)
                
            now = datetime.now(timezone.utc)
            diff_seconds = (published_at - now).total_seconds()
            diff_mins = diff_seconds / 60
            is_future = diff_seconds > 0
            
            print(f"IS FUTURE? {is_future}")
            print(f"DIFF: {diff_mins:.2f} minutes")
            
            if is_future:
                print("STATUS: ⏳ SCHEDULED (Hidden)")
            else:
                print("STATUS: ✅ PUBLISHED (Visible)")
        else:
             print("STATUS: 📝 DRAFT (No Date)")
    else:
        print("No posts found.")

print("\n-------------------")
