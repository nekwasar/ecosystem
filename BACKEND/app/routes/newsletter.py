from fastapi import APIRouter, Depends, HTTPException, Form, Request, BackgroundTasks, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from services.newsletter_service import NewsletterService
from schemas.blog import NewsletterSubscriberCreate, NewsletterCampaignCreate, NewsletterTemplateCreate, NewsletterSegmentCreate
from typing import Optional
import shutil
import os
from pathlib import Path
from datetime import datetime

router = APIRouter()

# Ensure uploads dir
# We need to save to the directory served by /static (which is mounted to PROJECT_ROOT/portfolio)
# This file is in BACKEND/app/routes/newsletter.py
# parents[0]=routes, parents[1]=app, parents[2]=BACKEND, parents[3]=ROOT
PROJECT_ROOT = Path(__file__).resolve().parents[3]
UPLOAD_DIR = PROJECT_ROOT / "portfolio" / "newsletter_uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Admin endpoints
@router.get("/admin/subscribers")
async def get_all_subscribers(db: Session = Depends(get_db)):
    """Get all newsletter subscribers (admin only)"""
    try:
        from models.blog import NewsletterSubscriber
        
        subscribers = db.query(NewsletterSubscriber).order_by(NewsletterSubscriber.subscribed_at.desc()).all()
        
        return {
            "success": True,
            "subscribers": [
                {
                    "id": sub.id,
                    "name": sub.name,
                    "email": sub.email,
                    "is_active": sub.is_active,
                    "subscribed_at": sub.subscribed_at.isoformat() if sub.subscribed_at else None,
                    "unsubscribed_at": sub.unsubscribed_at.isoformat() if sub.unsubscribed_at else None,
                }
                for sub in subscribers
            ]
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to get subscribers: {str(e)}")

@router.delete("/admin/subscribers/{subscriber_id}")
async def delete_subscriber(subscriber_id: int, db: Session = Depends(get_db)):
    """Delete a subscriber (admin only)"""
    try:
        from models.blog import NewsletterSubscriber
        
        subscriber = db.query(NewsletterSubscriber).filter(NewsletterSubscriber.id == subscriber_id).first()
        if not subscriber:
            raise HTTPException(404, "Subscriber not found")
        
        db.delete(subscriber)
        db.commit()
        
        return {
            "success": True,
            "message": "Subscriber deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Failed to delete subscriber: {str(e)}")


@router.post("/subscribe")
async def subscribe_newsletter(
    request: Request,
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    """Subscribe to newsletter - immediate activation, welcome email sent"""
    try:
        newsletter_service = NewsletterService(db)

        subscriber_data = NewsletterSubscriberCreate(
            name=name,
            email=email,
            preferences={}  # Can be extended later
        )

        result = await newsletter_service.subscribe_user(subscriber_data, background_tasks)

        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "subscriber_id": result["subscriber_id"]
            }
        else:
            return {
                "success": False,
                "message": result["message"],
                "subscriber_id": result.get("subscriber_id")
            }

    except Exception as e:
        raise HTTPException(500, f"Subscription failed: {str(e)}")

@router.post("/unsubscribe")
async def unsubscribe_newsletter(
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    """Unsubscribe from newsletter"""
    try:
        newsletter_service = NewsletterService(db)
        result = await newsletter_service.unsubscribe_user(email)

        return {
            "success": result["success"],
            "message": result["message"]
        }

    except Exception as e:
        raise HTTPException(500, f"Unsubscription failed: {str(e)}")

@router.get("/unsubscribe")
async def unsubscribe_via_link(
    email: str,
    db: Session = Depends(get_db)
):
    """Unsubscribe via link in newsletter (returns HTML page)"""
    try:
        newsletter_service = NewsletterService(db)
        result = await newsletter_service.unsubscribe_user(email)
        
        settings = newsletter_service.get_settings()
        site_name = settings.get("site_name", "Our Website")
        site_url = settings.get("site_url", "/")

        # Return HTML response
        if result["success"]:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Unsubscribed - {site_name}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f4f7f6; color: #333; }}
                    .card {{ background: white; padding: 40px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: inline-block; max-width: 500px; }}
                    .success {{ color: #28a745; }}
                    .message {{ font-size: 18px; margin: 20px 0; }}
                    .btn {{ display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; }}
                </style>
            </head>
            <body>
                <div class="card">
                    <h1 class="success">✓ Successfully Unsubscribed</h1>
                    <p class="message">{result["message"]}</p>
                    <p>We're sorry to see you go. You can always subscribe again if you change your mind.</p>
                    <a href="{site_url}" class="btn">Return to {site_name}</a>
                </div>
            </body>
            </html>
            """
        else:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Unsubscribe - {site_name}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f4f7f6; }}
                    .card {{ background: white; padding: 40px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: inline-block; max-width: 500px; }}
                    .error {{ color: #dc3545; }}
                    .message {{ font-size: 18px; margin: 20px 0; }}
                    .btn {{ display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; }}
                </style>
            </head>
            <body>
                <div class="card">
                    <h1 class="error">Unsubscribe Failed</h1>
                    <p class="message">{result["message"]}</p>
                    <a href="{site_url}" class="btn">Return to {site_name}</a>
                </div>
            </body>
            </html>
            """

        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=html_content)

    except Exception as e:
        settings_rows = db.execute(text("SELECT key, value FROM system_settings")).all()
        settings = {s[0]: s[1] for s in settings_rows}
        site_name = settings.get("site_name", "Our Website")
        site_url = settings.get("site_url", "/")
        
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error - {site_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error {{ color: #dc3545; }}
            </style>
        </head>
        <body>
            <h1 class="error">Error</h1>
            <p>Something went wrong. Please try again later.</p>
            <a href="{site_url}">Return home</a>
        </body>
        </html>
        """
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=error_html, status_code=500)

@router.post("/admin/send-weekly")
async def send_weekly_newsletter(db: Session = Depends(get_db)):
    """Manually trigger weekly newsletter (admin only)"""
    try:
        newsletter_service = NewsletterService(db)
        result = await newsletter_service.send_weekly_newsletter()

        return {
            "success": result["success"],
            "message": result["message"],
            "sent_count": result["sent_count"],
            "failed_count": result.get("failed_count", 0),
            "campaign_id": result.get("campaign_id")
        }

    except Exception as e:
        raise HTTPException(500, f"Weekly newsletter failed: {str(e)}")

@router.get("/admin/campaigns")
async def get_campaigns(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all campaigns (admin only)"""
    try:
        service = NewsletterService(db)
        campaigns = await service.get_campaigns(skip, limit)
        return {
            "success": True,
            "campaigns": [
                {
                    "id": c.id,
                    "name": c.name,
                    "subject": c.subject,
                    "status": c.status,
                    "templateType": c.template_type,
                    "scheduledAt": c.scheduled_at.isoformat() if c.scheduled_at else None,
                    "sentAt": c.sent_at.isoformat() if c.sent_at else None,
                    "recipientCount": c.recipient_count,
                    "openCount": c.open_count,
                    "clickCount": c.click_count,
                    "openRate": round((c.open_count / c.recipient_count * 100), 1) if c.recipient_count and c.recipient_count > 0 else 0,
                    "clickRate": round((c.click_count / c.recipient_count * 100), 1) if c.recipient_count and c.recipient_count > 0 else 0,
                    "createdAt": c.created_at.isoformat() if c.created_at else None
                } for c in campaigns
            ]
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to get campaigns: {str(e)}")

@router.get("/admin/campaigns/{campaign_id}")
async def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """Get single campaign details (admin only)"""
    try:
        service = NewsletterService(db)
        campaign = await service.get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(404, "Campaign not found")
        
        return {
            "success": True,
            "campaign": {
                "id": campaign.id,
                "name": campaign.name,
                "subject": campaign.subject,
                "content": campaign.content,
                "templateId": campaign.template_id,
                "templateType": campaign.template_type,
                "status": campaign.status,
                "segmentId": campaign.segment_id,
                "scheduledAt": campaign.scheduled_at.isoformat() if campaign.scheduled_at else None
            }
        }
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(500, str(e))

@router.post("/admin/campaigns")
async def create_campaign(
    campaign_data: NewsletterCampaignCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create newsletter campaign (admin only)"""
    try:
        # Debug log
        print(f"Creating campaign with: {campaign_data}")
        
        newsletter_service = NewsletterService(db)
        
        # If template_id is provided, try to fetch its content
        final_content = campaign_data.content
        if campaign_data.template_id:
            template = newsletter_service.get_template(campaign_data.template_id)
            if template:
                # Use template content if available, and if content wasn't explicitly provided (or is empty)
                if not final_content:
                    final_content = template.content_template
        
        # Update content in data object (if we modified it)
        if final_content:
            campaign_data.content = final_content
        
        campaign = await newsletter_service.create_campaign(campaign_data, background_tasks)

        return {
            "success": True,
            "message": "Campaign created successfully",
            "campaign_id": campaign.id
        }

    except Exception as e:
        print(f"Create Campaign Error: {e}")
        raise HTTPException(500, f"Campaign creation failed: {str(e)}")

@router.put("/admin/campaigns/{campaign_id}")
async def update_campaign(
    campaign_id: int,
    campaign_data: NewsletterCampaignCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Update newsletter campaign (admin only)"""
    try:
        service = NewsletterService(db)
        campaign = await service.update_campaign(campaign_id, campaign_data, background_tasks)
        return {
            "success": True,
            "message": "Campaign updated successfully",
            "campaign": {
                "id": campaign.id,
                "name": campaign.name,
                "status": campaign.status
            }
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@router.delete("/admin/campaigns/{campaign_id}")
async def delete_campaign(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """Delete newsletter campaign (admin only)"""
    try:
        service = NewsletterService(db)
        success = await service.delete_campaign(campaign_id)
        if success:
            return {"success": True, "message": "Campaign deleted"}
        raise HTTPException(404, "Campaign not found")
    except Exception as e:
        raise HTTPException(500, str(e))

# Template Management Endpoints
@router.post("/admin/templates")
async def create_template(
    template_data: NewsletterTemplateCreate,
    db: Session = Depends(get_db)
):
    """Create a new newsletter template (admin only)"""
    try:
        newsletter_service = NewsletterService(db)
        template = await newsletter_service.create_template(template_data)
        return {
            "success": True,
            "message": "Template created successfully",
            "template_id": template.id
        }
    except Exception as e:
        raise HTTPException(500, f"Template creation failed: {str(e)}")

@router.get("/admin/templates")
async def get_templates(
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all newsletter templates"""
    try:
        newsletter_service = NewsletterService(db)
        templates = newsletter_service.get_templates(skip, limit, category)
        return {
            "success": True,
            "templates": [
                {
                    "id": t.id,
                    "name": t.name,
                    "category": t.category,
                    "thumbnail_url": t.thumbnail_url,
                    "created_at": t.created_at.isoformat() if t.created_at else None
                }
                for t in templates
            ]
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to get templates: {str(e)}")

@router.get("/admin/templates/{template_id}")
async def get_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific template"""
    try:
        newsletter_service = NewsletterService(db)
        template = newsletter_service.get_template(template_id)
        if not template:
            raise HTTPException(404, "Template not found")
        
        return {
            "success": True,
            "template": {
                "id": template.id,
                "name": template.name,
                "subject_template": template.subject_template,
                "content_template": template.content_template,
                "category": template.category,
                "thumbnail_url": template.thumbnail_url,
                "created_at": template.created_at.isoformat() if template.created_at else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to get template: {str(e)}")

@router.put("/admin/templates/{template_id}")
async def update_template(
    template_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Update a newsletter template"""
    try:
        data = await request.json()
        newsletter_service = NewsletterService(db)
        template = await newsletter_service.update_template(template_id, data)
        
        if not template:
            raise HTTPException(404, "Template not found")
            
        return {
            "success": True,
            "message": "Template updated successfully",
            "template_id": template.id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Template update failed: {str(e)}")

@router.delete("/admin/templates/{template_id}")
async def delete_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """Delete a newsletter template"""
    try:
        newsletter_service = NewsletterService(db)
        success = await newsletter_service.delete_template(template_id)
        
        if not success:
            raise HTTPException(404, "Template not found")
            
        return {
            "success": True,
            "message": "Template deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Template deletion failed: {str(e)}")

@router.get("/stats")
async def get_newsletter_stats(db: Session = Depends(get_db)):
    """Get newsletter statistics"""
    try:
        newsletter_service = NewsletterService(db)
        stats = newsletter_service.get_subscriber_stats()

        return {
            "success": True,
            "stats": stats
        }

    except Exception as e:
        raise HTTPException(500, f"Failed to get stats: {str(e)}")

@router.get("/test-email")
async def test_email(
    email: str,
    db: Session = Depends(get_db)
):
    """Test email sending (development only)"""
    try:
        newsletter_service = NewsletterService(db)

        # Create test subscriber
        test_subscriber = type('TestSubscriber', (), {
            'name': 'Test User',
            'email': email
        })()

        # Send test welcome email
        await newsletter_service._send_welcome_email(test_subscriber)

        return {
            "success": True,
            "message": f"Test email sent to {email}"
        }

    except Exception as e:
        raise HTTPException(500, f"Test email failed: {str(e)}")

# System Settings & Automation Endpoints
@router.get("/admin/settings")
async def get_settings(db: Session = Depends(get_db)):
    """Get system settings"""
    try:
        service = NewsletterService(db)
        return {"success": True, "settings": service.get_settings()}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/admin/settings")
async def save_settings(request: Request, db: Session = Depends(get_db)):
    """Save system settings"""
    try:
        data = await request.json()
        service = NewsletterService(db)
        service.save_settings(data)
        return {"success": True, "message": "Settings saved"}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/admin/automations")
async def get_automations(db: Session = Depends(get_db)):
    """Get all automations"""
    try:
        service = NewsletterService(db)
        automations = service.get_automations()
        return {
            "success": True, 
            "automations": [
                {
                    "id": a.id,
                    "name": a.name,
                    "trigger_type": a.trigger_type,
                    "template_id": a.template_id,
                    "subject": a.subject,
                    "sender_name": a.sender_name,
                    "delay_hours": a.delay_hours,
                    "is_active": a.is_active
                } for a in automations
            ]
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/admin/automations/stats")
async def get_automation_stats(db: Session = Depends(get_db)):
    """Get automation monitoring stats"""
    try:
        service = NewsletterService(db)
        return {"success": True, "stats": service.get_automation_stats()}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/admin/automations")
async def create_automation(
    name: str = Form(...),
    subject: str = Form(...),
    sender_name: str = Form(...),
    trigger_type: str = Form(...),
    template_id: int = Form(...),
    delay_hours: int = Form(0),
    db: Session = Depends(get_db)
):
    """Create new automation"""
    try:
        service = NewsletterService(db)
        auto = await service.create_automation(name, trigger_type, template_id, delay_hours, subject, sender_name)
        return {"success": True, "message": "Automation created", "automation_id": auto.id}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.patch("/admin/automations/{auto_id}/toggle")
async def toggle_automation(auto_id: int, request: Request, db: Session = Depends(get_db)):
    """Toggle automation status"""
    try:
        data = await request.json()
        is_active = data.get('is_active', False)
        service = NewsletterService(db)
        await service.toggle_automation(auto_id, is_active)
        return {"success": True, "message": f"Automation {'enabled' if is_active else 'disabled'}"}
    except Exception as e:
        raise HTTPException(500, str(e))



@router.delete("/admin/automations/{auto_id}")
async def delete_automation(auto_id: int, db: Session = Depends(get_db)):
    """Delete automation"""
    try:
        service = NewsletterService(db)
        await service.delete_automation(auto_id)
        return {"success": True, "message": "Automation deleted"}
    except Exception as e:
        raise HTTPException(500, str(e))
@router.post("/webhook")
async def brevo_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Brevo Webhooks"""
    try:
        payload = await request.json()
        event = payload.get('event')
        tags = payload.get('tags', [])
        
        # Extract Campaign ID
        campaign_id = None
        if tags:
            for tag in tags:
                if tag.startswith('campaign_'):
                    try:
                        campaign_id = int(tag.split('_')[1])
                        break
                    except: pass
        
        if campaign_id:
            from models.blog import NewsletterCampaign
            campaign = db.query(NewsletterCampaign).filter(NewsletterCampaign.id == campaign_id).first()
            if campaign:
                # Update Stats
                if event == 'opened' or event == 'unique_opened':
                    campaign.open_count = (campaign.open_count or 0) + 1
                elif event == 'click' or event == 'valid_click':
                    campaign.click_count = (campaign.click_count or 0) + 1
                
                # We could also track soft/hard bounces to update subscriber status
                
                db.commit()
                
        return {"success": True}
    except Exception as e:
        print(f"Webhook Error: {str(e)}")
        return {"success": False}

from fastapi import File, UploadFile
import shutil
import os
from pathlib import Path

# Ensure static directory exists
UPLOAD_DIR = Path("static/newsletter_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/admin/upload")
async def upload_image(file: UploadFile = File(...)):
    """Upload an image for newsletter"""
    try:
        # Generate safe filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        safe_name = f"{timestamp}_{file.filename.replace(' ', '_')}"
        file_location = UPLOAD_DIR / safe_name
        
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Return URL (assuming /static mount)
        # We need to know the domain, but relative URL /static/... usually works for frontend
        return {"success": True, "url": f"/static/newsletter_uploads/{safe_name}"}
    except Exception as e:
        print(f"Upload failed: {e}")
        return {"success": False, "error": str(e)}

@router.get("/admin/segments")
async def get_segments(db: Session = Depends(get_db)):
    """Get all segments"""
    try:
        service = NewsletterService(db)
        segments = service.get_segments()
        return {
            "success": True, 
            "segments": [
                {
                    "id": s.id,
                    "name": s.name,
                    "type": s.type,
                    "criteria": s.criteria,
                    "description": s.description,
                    "cached_count": s.cached_count,
                    "last_calcd_at": s.last_calcd_at.isoformat() if s.last_calcd_at else None,
                    "created_at": s.created_at.isoformat() if s.created_at else None
                } for s in segments
            ]
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/admin/segments")
async def create_segment(segment: NewsletterSegmentCreate, db: Session = Depends(get_db)):
    """Create a new segment"""
    try:
        service = NewsletterService(db)
        new_seg = service.create_segment(segment)
        return {"success": True, "segment": new_seg}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.delete("/admin/segments/{segment_id}")
async def delete_segment(segment_id: int, db: Session = Depends(get_db)):
    """Delete a segment"""
    try:
        service = NewsletterService(db)
        success = service.delete_segment(segment_id)
        if success:
            return {"success": True}
        raise HTTPException(404, "Segment not found")
    except Exception as e:
        raise HTTPException(500, str(e))
