
import sys
import os
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add current dir to path
sys.path.append(os.getcwd())

from models.blog import NewsletterCampaign
from core.config import settings

def diagnose_scheduler():
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    db = Session()

    now_utc = datetime.now(timezone.utc)
    print(f"Current System Time (UTC): {now_utc}")

    # Check all scheduled campaigns
    campaigns = db.query(NewsletterCampaign).filter(NewsletterCampaign.status == "scheduled").all()
    
    print(f"\nFound {len(campaigns)} campaigns with status 'scheduled':")
    
    for c in campaigns:
        print(f"--- Campaign ID: {c.id} ('{c.name}') ---")
        print(f"Status: {c.status}")
        print(f"Scheduled At (from DB): {c.scheduled_at}")
        
        if c.scheduled_at:
            # Check tzinfo
            tz = c.scheduled_at.tzinfo
            print(f"Timezone info: {tz if tz else 'Naive (None)'}")
            
            # Compare
            sch_at = c.scheduled_at
            if sch_at.tzinfo is None:
                sch_at = sch_at.replace(tzinfo=timezone.utc)
            
            if sch_at <= now_utc:
                print(f"RESULT: Should have sent! ({sch_at} <= {now_utc})")
            else:
                diff = sch_at - now_utc
                print(f"RESULT: Still in the future. {diff} remaining.")
        else:
            print("RESULT: ERROR - scheduled_at is NULL but status is 'scheduled'")

    db.close()

if __name__ == "__main__":
    diagnose_scheduler()
