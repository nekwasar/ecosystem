import logging
from typing import List, Optional, Dict
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from fastapi import BackgroundTasks

from core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        if not settings.brevo_api_key:
            logger.warning("Brevo API key not configured. Email sending will be disabled.")
            self.api_instance = None
            return

        self.configuration = sib_api_v3_sdk.Configuration()
        self.configuration.api_key['api-key'] = settings.brevo_api_key
        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(self.configuration))
        self.sender = {"name": settings.sender_name, "email": settings.sender_email}

    def send_transactional_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str, 
        to_name: Optional[str] = None,
        reply_to: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Send a single transactional email.
        """
        if not self.api_instance:
            logger.error("Email service not initialized (missing API key)")
            return False

        try:
            to_contact = {"email": to_email}
            if to_name:
                to_contact["name"] = to_name

            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[to_contact],
                sender=self.sender,
                subject=subject,
                html_content=html_content,
                reply_to=reply_to,
                tags=tags
            )

            api_response = self.api_instance.send_transac_email(send_smtp_email)
            logger.info(f"Email sent successfully to {to_email}. Message ID: {api_response.message_id}")
            return True
        except ApiException as e:
            logger.error(f"Exception when calling TransactionalEmailsApi->send_transac_email: {e}")
            return False

    def send_batch_email(
        self, 
        recipients: List[Dict[str, str]], 
        subject: str, 
        html_content: str
    ) -> int:
        """
        Send a batch of emails. 
        Note: Brevo recommends using Campaigns for large sends, but for free plan <300/day,
        batch transactional is okay if within limits.
        
        recipients: List of dicts with 'email' and optional 'name'.
        Returns: Number of successfully queued emails.
        """
        if not self.api_instance:
            return 0

        success_count = 0
        # Brevo allows multiple recipients in one transactional call, but they all see each other unless Bcc.
        # OR we can loop. For strictly personal emails (like newsletters), looping is safer 
        # to prevent data leakage, OR use 'messageVersions' for individual customization in one call.
        # Given the 300 limit, individual calls are acceptable but slow. 
        # Let's use individual calls for now to ensure personalization safety.
        
        for recipient in recipients:
            sent = self.send_transactional_email(
                to_email=recipient['email'],
                to_name=recipient.get('name'),
                subject=subject,
                html_content=html_content
            )
            if sent:
                success_count += 1
        
        return success_count

    async def send_email_background(
        self, 
        background_tasks: BackgroundTasks,
        to_email: str, 
        subject: str, 
        html_content: str,
        to_name: Optional[str] = None,
        reply_to: Optional[Dict[str, str]] = None
    ):
        """
        Helper to schedule email sending in background.
        """
        background_tasks.add_task(
            self.send_transactional_email, 
            to_email, 
            subject, 
            html_content, 
            to_name,
            reply_to
        )

# Global instance
email_service = EmailService()
