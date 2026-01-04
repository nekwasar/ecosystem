from sqlalchemy import create_engine, text, inspect
from core.config import settings
import os
import sys

# Ensure we can import from app
sys.path.append(os.getcwd())

from database import Base, engine
# Import ALL models so Base.metadata knows about them
from models.blog import NewsletterCampaign, NewsletterTemplate, SystemSetting

def update_schema():
    print("🔄 Checking database schema...")
    
    # 1. Ensure tables exist first
    print("   🔨 Ensuring base tables exist...")
    Base.metadata.create_all(bind=engine)
    
    inspector = inspect(engine)
    
    with engine.connect() as connection:
        # 1. newsletter_campaigns
        if inspector.has_table("newsletter_campaigns"):
            columns = [c['name'] for c in inspector.get_columns('newsletter_campaigns')]
            print(f"   Current columns in newsletter_campaigns: {columns}")
            
            if 'template_id' not in columns:
                 print("   ➕ Adding template_id to newsletter_campaigns")
                 connection.execute(text("ALTER TABLE newsletter_campaigns ADD COLUMN template_id INTEGER"))
                 connection.commit()
                 
            if 'customized_html' not in columns:
                 print("   ➕ Adding customized_html to newsletter_campaigns")
                 connection.execute(text("ALTER TABLE newsletter_campaigns ADD COLUMN customized_html TEXT"))
                 connection.commit()

            if 'open_count' not in columns:
                 print("   ➕ Adding open_count to newsletter_campaigns")
                 connection.execute(text("ALTER TABLE newsletter_campaigns ADD COLUMN open_count INTEGER DEFAULT 0"))
                 connection.commit()

            if 'click_count' not in columns:
                 print("   ➕ Adding click_count to newsletter_campaigns")
                 connection.execute(text("ALTER TABLE newsletter_campaigns ADD COLUMN click_count INTEGER DEFAULT 0"))
                 connection.commit()

            if 'segment_id' not in columns:
                 print("   ➕ Adding segment_id to newsletter_campaigns")
                 connection.execute(text("ALTER TABLE newsletter_campaigns ADD COLUMN segment_id INTEGER"))
                 connection.commit()

        # 2. newsletter_templates
        if inspector.has_table("newsletter_templates"):
            columns = [c['name'] for c in inspector.get_columns('newsletter_templates')]
            print(f"   Current columns in newsletter_templates: {columns}")

            if 'category' not in columns:
                 print("   ➕ Adding category to newsletter_templates")
                 connection.execute(text("ALTER TABLE newsletter_templates ADD COLUMN category VARCHAR(50)"))
                 connection.commit()
            
            if 'description' not in columns:
                 print("   ➕ Adding description to newsletter_templates")
                 connection.execute(text("ALTER TABLE newsletter_templates ADD COLUMN description TEXT"))
                 connection.commit()
                 
            if 'thumbnail_url' not in columns:
                 print("   ➕ Adding thumbnail_url to newsletter_templates")
                 connection.execute(text("ALTER TABLE newsletter_templates ADD COLUMN thumbnail_url VARCHAR(500)"))
                 connection.commit()

        # 3. system_settings
        if inspector.has_table("system_settings"):
            print("   ✅ system_settings table exists")
        else:
            print("   ⚠️ system_settings missing even after create_all?")

    print("✅ Database schema updated successfully!")

if __name__ == "__main__":
    update_schema()
