from app.database import SessionLocal
from app.models.blog import BlogPost
from datetime import datetime, timezone
import sys
import os

# Add the parent directory to sys.path to allow imports from 'app'
sys.path.append(os.getcwd())

db = SessionLocal()
print(f"SERVER TIME (UTC): {datetime.now(timezone.utc)}")

# Get the most recently created post
post = db.query(BlogPost).order_by(BlogPost.id.desc()).first()

if post:
    print(f"\n--- LATEST POST ---")
    print(f"ID: {post.id}")
    print(f"TITLE: {post.title}")
    print(f"SLUG: {post.slug}")
    print(f"PUBLISHED_AT (DB): {post.published_at}")
    
    if post.published_at:
        # Ensure aware
        p_at = post.published_at
        if p_at.tzinfo is None:
            p_at = p_at.replace(tzinfo=timezone.utc)
            
        now = datetime.now(timezone.utc)
        
        # Calculate diff
        diff_seconds = (p_at - now).total_seconds()
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
