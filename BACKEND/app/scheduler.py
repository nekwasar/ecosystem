from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from services.newsletter_service import NewsletterService
from database import get_db
from sqlalchemy.orm import Session
from models.blog import BlogLike, TemporalUser as TemporalUserModel, BlogPost as BlogPostModel
from sqlalchemy import func
import asyncio
import logging

logger = logging.getLogger("scheduler")
logger.setLevel(logging.INFO)

scheduler = AsyncIOScheduler()

async def send_weekly_newsletter_job():
    """Scheduled job to send weekly newsletter every Monday at 9 AM"""
    try:
        # Get database session
        db = next(get_db())

        # Create newsletter service and send
        newsletter_service = NewsletterService(db)
        result = await newsletter_service.send_weekly_newsletter()
        logger.info(f"Weekly newsletter job completed: {result}")

    except Exception as e:
        print(f"Weekly newsletter job failed: {e}")
    finally:
        db.close()

async def check_scheduled_campaigns_job():
    """Job to check for and send scheduled campaigns every minute"""
    try:
        db = next(get_db())
        newsletter_service = NewsletterService(db)
        logger.info("Checking for scheduled campaigns...")
        await newsletter_service.process_scheduled_campaigns()
    except Exception as e:
        logger.error(f"Scheduled campaigns check failed: {e}", exc_info=True)
    finally:
        db.close()

async def cleanup_expired_data_job():
    """Scheduled job to cleanup expired likes and temporal users daily at 2 AM"""
    try:
        # Get database session
        db = next(get_db())
        
        # Cleanup expired likes - REMOVED (Likes are now permanent)
        # try:
        #     # Logic removed
        #     pass
        # except Exception as e:
        #     pass
        
        # Cleanup expired temporal users
        try:
            expired_count = db.query(TemporalUserModel).filter(
                TemporalUserModel.expires_at <= func.now()
            ).delete()
            print(f"Cleaned up {expired_count} expired temporal users")
            
        except Exception as e:
            print(f"Expired temporal users cleanup failed: {e}")
        
        db.commit()
        
    except Exception as e:
        print(f"Cleanup job failed: {e}")
    finally:
        db.close()

async def automation_queue_job():
    """Check and process the automation queue every minute"""
    db = next(get_db())
    try:
        from services.newsletter_service import NewsletterService
        service = NewsletterService(db)
        await service.process_automation_queue()
    except Exception as e:
        logger.error(f"Automation queue processing failed: {e}")
    finally:
        db.close()

def init_scheduler():
    """Initialize the scheduler with jobs"""
    # Schedule weekly newsletter for every Monday at 9:00 AM
    scheduler.add_job(
        send_weekly_newsletter_job,
        trigger=CronTrigger(day_of_week='mon', hour=9),
        id='weekly_newsletter',
        name='Send Weekly Newsletter',
        replace_existing=True
    )
    
    # Schedule daily cleanup of expired likes and temporal users at 2:00 AM
    scheduler.add_job(
        cleanup_expired_data_job,
        trigger=CronTrigger(hour=2, minute=0),
        id='cleanup_expired_data',
        name='Cleanup Expired Likes and Users',
        replace_existing=True
    )

    # Schedule check for scheduled campaigns every minute
    scheduler.add_job(
        check_scheduled_campaigns_job,
        trigger=CronTrigger(second=0), # Runs at the start of every minute
        id='check_scheduled',
        name='Check Scheduled Campaigns',
        replace_existing=True
    )

    # Schedule check for automation queue every minute
    scheduler.add_job(
        automation_queue_job,
        trigger=CronTrigger(second=30), # Offset by 30 seconds to split the load
        id='automation_queue',
        name='Process Automation Queue',
        replace_existing=True
    )

    print("Scheduler initialized:")
    print("- Weekly newsletter scheduled for every Monday at 9 AM")
    print("- Daily cleanup scheduled for every day at 2 AM")
    print("- Scheduled campaigns check set for every minute")
    print("- Automation queue check set for every minute (offset by 30s)")
    
    # Log registered jobs for verification
    for job in scheduler.get_jobs():
        next_run = getattr(job, 'next_run_time', 'Unknown')
        logger.info(f"Registered Job: {job.id} - Next run: {next_run}")

def start_scheduler():
    """Start the scheduler"""
    if not scheduler.running:
        scheduler.start()
        print("Newsletter scheduler started")

def stop_scheduler():
    """Stop the scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        print("Newsletter scheduler stopped")

# For testing - send newsletter immediately
async def send_newsletter_now():
    """Manually trigger newsletter sending for testing"""
    await send_weekly_newsletter_job()

if __name__ == "__main__":
    # For testing the scheduler
    import asyncio
    asyncio.run(send_newsletter_now())