from fastapi import APIRouter, Depends, HTTPException, Form, Request, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db
from services.newsletter_service import NewsletterService
from schemas.blog import NewsletterSubscriberCreate, NewsletterCampaignCreate, NewsletterTemplateCreate
from typing import Optional

router = APIRouter()

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

        # Return HTML response
        if result["success"]:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Unsubscribed - NekwasaR Blog</title>
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                    .success {{ color: #28a745; }}
                    .message {{ font-size: 18px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <h1 class="success">✓ Successfully Unsubscribed</h1>
                <p class="message">{result["message"]}</p>
                <p>We're sorry to see you go. You can always subscribe again if you change your mind.</p>
                <a href="https://nekwasar.com/blog">Visit Our Blog</a>
            </body>
            </html>
            """
        else:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Unsubscribe - NekwasaR Blog</title>
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                    .error {{ color: #dc3545; }}
                    .message {{ font-size: 18px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <h1 class="error">Unsubscribe Failed</h1>
                <p class="message">{result["message"]}</p>
                <a href="https://nekwasar.com/blog">Visit Our Blog</a>
            </body>
            </html>
            """

        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=html_content)

    except Exception as e:
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error - NekwasaR Blog</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error {{ color: #dc3545; }}
            </style>
        </head>
        <body>
            <h1 class="error">Error</h1>
            <p>Something went wrong. Please try again later.</p>
            <a href="https://nekwasar.com/blog">Visit Our Blog</a>
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
                    "subject": c.subject,
                    "status": c.status,
                    "template_type": c.template_type,
                    "scheduled_at": c.scheduled_at.isoformat() if c.scheduled_at else None,
                    "sent_at": c.sent_at.isoformat() if c.sent_at else None,
                    "recipient_count": c.recipient_count,
                    "open_count": c.open_count,
                    "click_count": c.click_count,
                    "openRate": round((c.open_count / c.recipient_count * 100), 1) if c.recipient_count and c.recipient_count > 0 else 0,
                    "clickRate": round((c.click_count / c.recipient_count * 100), 1) if c.recipient_count and c.recipient_count > 0 else 0,
                    "created_at": c.created_at.isoformat() if c.created_at else None
                } for c in campaigns
            ]
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to get campaigns: {str(e)}")

@router.post("/admin/campaigns")
async def create_campaign(
    subject: str = Form(...),
    content: Optional[str] = Form(None),
    template_type: str = Form("custom"),
    template_id: Optional[int] = Form(None),
    scheduled_at: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Create newsletter campaign (admin only)"""
    try:
        from datetime import datetime
        
        newsletter_service = NewsletterService(db)
        
        # If template_id is provided, try to fetch its content
        final_content = content
        if template_id:
            template = newsletter_service.get_template(template_id)
            if template:
                # Use template content if available, and if content wasn't explicitly provided (or is empty)
                if not final_content:
                    final_content = template.content_template
        
        campaign_data = NewsletterCampaignCreate(
            subject=subject,
            content=final_content or "", # Ensure we have string
            template_type=template_type,
            template_id=template_id,
            scheduled_at=datetime.fromisoformat(scheduled_at) if scheduled_at else None
        )

        campaign = await newsletter_service.create_campaign(campaign_data)

        return {
            "success": True,
            "message": "Campaign created successfully",
            "campaign_id": campaign.id
        }

    except Exception as e:
        raise HTTPException(500, f"Campaign creation failed: {str(e)}")

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
                    "delay_hours": a.delay_hours,
                    "is_active": a.is_active
                } for a in automations
            ]
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/admin/automations")
async def create_automation(
    name: str = Form(...),
    trigger_type: str = Form(...),
    template_id: int = Form(...),
    delay_hours: int = Form(0),
    db: Session = Depends(get_db)
):
    """Create new automation"""
    try:
        service = NewsletterService(db)
        auto = await service.create_automation(name, trigger_type, template_id, delay_hours)
        return {"success": True, "message": "Automation created", "automation_id": auto.id}
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
