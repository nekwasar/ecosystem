import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks

from models.blog import NewsletterSubscriber, NewsletterCampaign, BlogPost, NewsletterTemplate, NewsletterAutomation, SystemSetting, NewsletterSegment
from schemas.blog import NewsletterSubscriberCreate, NewsletterCampaignCreate, NewsletterTemplateCreate, NewsletterSegmentCreate
from services.email_service import email_service

logger = logging.getLogger(__name__)

class NewsletterService:
    def __init__(self, db: Session):
        self.db = db

    async def subscribe_user(self, subscriber_data: NewsletterSubscriberCreate, background_tasks: BackgroundTasks) -> Dict[str, Any]:
        """Subscribe a user and trigger welcome automation"""
        try:
            # Check if already subscribed
            existing = self.db.query(NewsletterSubscriber).filter(
                NewsletterSubscriber.email == subscriber_data.email
            ).first()

            if existing:
                if existing.is_active:
                    return {
                        "success": False,
                        "message": "You're already subscribed to our newsletter!",
                        "subscriber_id": existing.id
                    }
                else:
                    # Reactivate
                    existing.is_active = True
                    existing.name = subscriber_data.name # Update name if changed
                    self.db.commit()
                    # Resend welcome? Maybe not if they unsubbed before. Let's treat as simple reactivation.
                    return {
                        "success": True,
                        "message": "Welcome back! Your subscription has been reactivated.",
                        "subscriber_id": existing.id
                    }

            # Create new subscriber
            subscriber = NewsletterSubscriber(
                name=subscriber_data.name,
                email=subscriber_data.email,
                preferences=subscriber_data.preferences or {},
                is_active=True
            )

            self.db.add(subscriber)
            self.db.commit()
            self.db.refresh(subscriber)

            # Trigger Welcome Automation
            # We look for an active automation rule for 'welcome'
            welcome_auto = self.db.query(NewsletterAutomation).filter(
                NewsletterAutomation.trigger_type == 'welcome',
                NewsletterAutomation.is_active == True
            ).first()

            if welcome_auto and welcome_auto.template_id:
                # Use the configured template
                await self._send_content_email(subscriber, welcome_auto.template_id, is_automation=True, background_tasks=background_tasks)
            else:
                # Fallback to hardcoded regular welcome if no automation is set up yet
                await self._send_welcome_email(subscriber, background_tasks)

            return {
                "success": True,
                "message": "Successfully subscribed! Check your email for a welcome message.",
                "subscriber_id": subscriber.id
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Subscription failed: {e}")
            raise Exception(f"Subscription failed: {str(e)}")

    async def unsubscribe_user(self, email: str) -> Dict[str, Any]:
        """Unsubscribe a user"""
        try:
            subscriber = self.db.query(NewsletterSubscriber).filter(
                NewsletterSubscriber.email == email,
                NewsletterSubscriber.is_active == True
            ).first()

            if not subscriber:
                return {"success": False, "message": "Email not found in our subscriber list."}

            subscriber.is_active = False
            subscriber.unsubscribed_at = datetime.now()
            self.db.commit()

            return {"success": True, "message": "Successfully unsubscribed from our newsletter."}

        except Exception as e:
            self.db.rollback()
            raise Exception(f"Unsubscription failed: {str(e)}")

    async def get_campaigns(self, skip: int = 0, limit: int = 100) -> List[NewsletterCampaign]:
        """Get all campaigns"""
        return self.db.query(NewsletterCampaign).order_by(NewsletterCampaign.created_at.desc()).offset(skip).limit(limit).all()

    async def create_campaign(self, campaign_data: NewsletterCampaignCreate, background_tasks: Optional[BackgroundTasks] = None) -> NewsletterCampaign:
        """Create and optionally SEND a newsletter campaign"""
        try:
            # Create the campaign record
            campaign = NewsletterCampaign(**campaign_data.dict())
            if not campaign.status:
                campaign.status = "draft"
            
            self.db.add(campaign)
            self.db.commit()
            self.db.refresh(campaign)

            # Check if it should be sent immediately
            # Logic: If scheduled_at is None (Immediate) AND status is NOT 'draft' (user clicked Send Now in Wizard?)
            # Actually, let's assume if the user hits the "Send Now" endpoint, they want to send it.
            # But the Controller (endpoint) determines intent.
            # Let's check if scheduled_at is NULL or in Past, we trigger send
            
            should_send_now = campaign.scheduled_at is None
            
            if should_send_now:
                # Update status to 'sending'
                campaign.status = "sending"
                self.db.commit()

                # Trigger sending
                # If we have background tasks, use them to avoid blocking the API
                if background_tasks:
                    background_tasks.add_task(self._execute_campaign_send, campaign.id)
                else: 
                     # Fallback for sync execution (e.g. tests)
                     await self._execute_campaign_send(campaign.id)

            return campaign
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Campaign creation failed: {str(e)}")

    async def _execute_campaign_send(self, campaign_id: int):
        """Internal method to process the sending of a campaign"""
        try:
            campaign = self.db.query(NewsletterCampaign).filter(NewsletterCampaign.id == campaign_id).first()
            if not campaign: return

            # Get target audience (active subscribers)
            subscribers = self.db.query(NewsletterSubscriber).filter(NewsletterSubscriber.is_active == True).all()
            
            # Fetch Custom Sender Settings if available
            system_settings = self.db.query(SystemSetting).first()
            sender_config = None
            if system_settings and system_settings.sender_email:
                sender_config = {"name": system_settings.sender_name, "email": system_settings.sender_email}

            sent_count = 0
            for sub in subscribers:
                # Basic personalization (could be expanded with Jinja within the content if needed)
                # But typically we just send the static HTML or simple str.replace
                
                content_html = campaign.customized_html or campaign.content
                content_html = content_html.replace("{{name}}", sub.name).replace("{{email}}", sub.email)
                
                # Use Transactional batch or single? We'll do single loop for now as per EmailService design logic
                email_service.send_transactional_email(
                    to_email=sub.email,
                    to_name=sub.name,
                    subject=campaign.subject,
                    html_content=content_html,
                    tags=[f"campaign_{campaign.id}"],
                    sender=sender_config
                )
                sent_count += 1
            
            # Done
            campaign.status = "sent"
            campaign.sent_at = datetime.now()
            campaign.recipient_count = sent_count
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Campaign send failed: {e}")
            if campaign:
                campaign.status = "failed"
                self.db.commit()

    # Template Management
    async def create_template(self, template_data: NewsletterTemplateCreate) -> NewsletterTemplate:
        """Create a new newsletter template"""
        try:
            template = NewsletterTemplate(**template_data.dict())
            self.db.add(template)
            self.db.commit()
            self.db.refresh(template)
            return template
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Template creation failed: {str(e)}")

    def get_templates(self, skip: int = 0, limit: int = 100, category: Optional[str] = None) -> List[NewsletterTemplate]:
        """Get all newsletter templates"""
        query = self.db.query(NewsletterTemplate).filter(NewsletterTemplate.is_active == True)
        if category:
            query = query.filter(NewsletterTemplate.category == category)
        return query.order_by(NewsletterTemplate.created_at.desc()).offset(skip).limit(limit).all()

    def get_template(self, template_id: int) -> Optional[NewsletterTemplate]:
        """Get a specific template by ID"""
        return self.db.query(NewsletterTemplate).filter(
            NewsletterTemplate.id == template_id,
            NewsletterTemplate.is_active == True
        ).first()

    async def update_template(self, template_id: int, template_data: Dict[str, Any]) -> Optional[NewsletterTemplate]:
        """Update a newsletter template"""
        try:
            template = self.get_template(template_id)
            if not template:
                return None
            
            for key, value in template_data.items():
                if hasattr(template, key):
                    setattr(template, key, value)
            
            self.db.commit()
            self.db.refresh(template)
            return template
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Template update failed: {str(e)}")

    async def delete_template(self, template_id: int) -> bool:
        """Soft delete a template"""
        try:
            template = self.get_template(template_id)
            if not template:
                return False
            
            template.is_active = False
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Template deletion failed: {str(e)}")

    def get_subscriber_stats(self) -> Dict[str, Any]:
        """Get newsletter subscriber statistics"""
        try:
            total = self.db.query(NewsletterSubscriber).count()
            active = self.db.query(NewsletterSubscriber).filter(
                NewsletterSubscriber.is_active == True
            ).count()

            # Get recent subscriptions (last 30 days)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent = self.db.query(NewsletterSubscriber).filter(
                NewsletterSubscriber.subscribed_at >= thirty_days_ago
            ).count()

            return {
                "total_subscribers": total,
                "active_subscribers": active,
                "inactive_subscribers": total - active,
                "recent_subscriptions": recent
            }
        except Exception as e:
            raise Exception(f"Failed to get subscriber stats: {str(e)}")

    async def _send_content_email(self, subscriber: NewsletterSubscriber, template_id: int, is_automation: bool = False, background_tasks: Optional[BackgroundTasks] = None):
        """Helper to send an email based on a Template ID"""
        template = self.get_template(template_id)
        if not template:
            logger.warning(f"Template {template_id} not found for sending to {subscriber.email}")
            return

        unsubscribe_url = f"https://nekwasar.com/api/newsletter/unsubscribe?email={subscriber.email}"
        
        # Render
        subject = template.subject_template
        content = template.content_template.replace("{{name}}", subscriber.name).replace("{{unsubscribe_url}}", unsubscribe_url)

        if background_tasks:
            # Use background sender
             background_tasks.add_task(
                email_service.send_transactional_email,
                subscriber.email,
                subject,
                content,
                subscriber.name
            )
        else:
            email_service.send_transactional_email(
                to_email=subscriber.email,
                to_name=subscriber.name,
                subject=subject,
                html_content=content
            )

    async def _send_welcome_email(self, subscriber: NewsletterSubscriber, background_tasks: Optional[BackgroundTasks] = None):
        """Legacy fallback welcome email"""
        subject = "Welcome to NekwasaR Blog! 🎉"
        unsubscribe_url = f"https://nekwasar.com/api/newsletter/unsubscribe?email={subscriber.email}"

        content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #333; text-align: center;">Welcome to NekwasaR Blog! 🎉</h1>
            <p>Hi {subscriber.name},</p>
            <p>Thanks for subscribing!</p>
            <p><a href="{unsubscribe_url}">Unsubscribe</a></p>
        </div>
        """
        
        if background_tasks:
             background_tasks.add_task(
                email_service.send_transactional_email,
                subscriber.email,
                subject,
                content,
                subscriber.name
            )
        else:
            email_service.send_transactional_email(
                to_email=subscriber.email,
                to_name=subscriber.name,
                subject=subject,
                html_content=content
            )

    def _get_weekly_content(self) -> str:
        """Generate weekly newsletter content from recent posts"""
        try:
            # Get recent posts from the last week
            week_ago = datetime.now() - timedelta(days=7)
            recent_posts = self.db.query(BlogPost).filter(
                BlogPost.published_at >= week_ago,
                BlogPost.is_featured == True
            ).order_by(BlogPost.published_at.desc()).limit(5).all()

            if not recent_posts:
                # Fallback to any recent posts
                recent_posts = self.db.query(BlogPost).filter(
                    BlogPost.published_at >= week_ago
                ).order_by(BlogPost.published_at.desc()).limit(5).all()

            # Build newsletter content
            content_parts = []

            if recent_posts:
                content_parts.append("<h2>This Week's Highlights</h2>")
                for post in recent_posts:
                    content_parts.append(f"<div><h3><a href='https://nekwasar.com/blog/{post.slug}'>{post.title}</a></h3><p>{post.excerpt}</p></div>")
            else:
                content_parts.append("""
                <h2>This Week's Highlights</h2>
                <p>We're working on some exciting new content! Stay tuned for our next update.</p>
                """)

            return "\n".join(content_parts)

        except Exception as e:
            return "<h2>Weekly Update</h2><p>Check our website for updates!</p>"

    # --- Settings Management (Database) ---
    def get_settings(self) -> Dict[str, Any]:
        """Get global newsletter settings"""
        default_settings = {
            "sender_name": "NekwasaR Team",
            "sender_email": "newsletter@nekwasar.com"
        }
        
        try:
            settings_rows = self.db.query(SystemSetting).all()
            db_settings = {s.key: s.value for s in settings_rows}
            return {**default_settings, **db_settings}
        except Exception as e:
            logger.error(f"Failed to load settings from DB: {e}")
            return default_settings

    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """Save global newsletter settings"""
        try:
            for key, value in settings.items():
                setting = self.db.query(SystemSetting).filter(SystemSetting.key == key).first()
                if setting:
                    setting.value = str(value)
                else:
                    setting = SystemSetting(key=key, value=str(value))
                    self.db.add(setting)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to save settings: {str(e)}")

    # --- Automation Management ---
    async def create_automation(self, name: str, trigger_type: str, template_id: int, delay_hours: int = 0) -> NewsletterAutomation:
        """Create a new automation rule"""
        try:
            # Deactivate existing automations of same type if we want single-active rule per type logic?
            # For 'welcome', typically only one is active.
            if trigger_type == 'welcome':
                existing = self.db.query(NewsletterAutomation).filter(
                    NewsletterAutomation.trigger_type == 'welcome',
                    NewsletterAutomation.is_active == True
                ).all()
                for e in existing:
                    e.is_active = False
            
            auto = NewsletterAutomation(
                name=name,
                trigger_type=trigger_type,
                template_id=template_id,
                delay_hours=delay_hours,
                is_active=True
            )
            self.db.add(auto)
            self.db.commit()
            self.db.refresh(auto)
            return auto
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Automation creation failed: {str(e)}")

    def get_automations(self) -> List[NewsletterAutomation]:
        """Get all active automations"""
        return self.db.query(NewsletterAutomation).filter(NewsletterAutomation.is_active == True).order_by(NewsletterAutomation.created_at.desc()).all()

    async def delete_automation(self, automation_id: int) -> bool:
        """Soft delete an automation"""
        try:
            auto = self.db.query(NewsletterAutomation).filter(NewsletterAutomation.id == automation_id).first()
            if auto:
                auto.is_active = False
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Automation deletion failed: {str(e)}")

    def get_segments(self) -> List[NewsletterSegment]:
        """Get all segments and refresh their counts"""
        segments = self.db.query(NewsletterSegment).order_by(NewsletterSegment.created_at.desc()).all()
        for seg in segments:
            try:
                # Recalculate count
                count = self.calculate_segment_size(seg.criteria)
                if seg.cached_count != count:
                    seg.cached_count = count
                    seg.last_calcd_at = datetime.now()
            except Exception as e:
                logger.error(f"Failed to calc size for segment {seg.id}: {e}")
        
        self.db.commit()
        return segments

    def create_segment(self, segment_data: NewsletterSegmentCreate) -> NewsletterSegment:
        """Create a new segment"""
        try:
            count = self.calculate_segment_size(segment_data.criteria)
            segment = NewsletterSegment(
                name=segment_data.name,
                type=segment_data.type,
                description=segment_data.description,
                criteria=segment_data.criteria,
                cached_count=count,
                last_calcd_at=datetime.now()
            )
            self.db.add(segment)
            self.db.commit()
            self.db.refresh(segment)
            return segment
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Segment creation failed: {str(e)}")

    def delete_segment(self, segment_id: int) -> bool:
        """Delete a segment"""
        try:
            seg = self.db.query(NewsletterSegment).filter(NewsletterSegment.id == segment_id).first()
            if seg:
                self.db.delete(seg)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Segment deletion failed: {str(e)}")

    def calculate_segment_size(self, criteria: Dict[str, Any]) -> int:
        """Calculate segment size based on criteria"""
        query = self.db.query(NewsletterSubscriber).filter(NewsletterSubscriber.is_active == True)
        
        if not criteria:
            return query.count()
            
        field = criteria.get('field')
        op = criteria.get('op')
        value = criteria.get('value')
        
        if field == 'email' and op == 'contains' and value:
            query = query.filter(NewsletterSubscriber.email.like(f"%{value}%"))
        elif field == 'name' and op == 'contains' and value:
             query = query.filter(NewsletterSubscriber.name.like(f"%{value}%"))
        elif field == 'is_confirmed' and op == 'eq':
             val = str(value).lower() == 'true'
             query = query.filter(NewsletterSubscriber.is_confirmed == val)
        # Add more logic as necessary (e.g., date ranges)
        
        return query.count()