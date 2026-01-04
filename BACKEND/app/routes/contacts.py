from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from models.contact import Contact as DBContact
from schemas import ContactCreate, Contact
from auth import get_current_active_user
from models.user import AdminUser
from services.email_service import email_service
from core.config import settings

router = APIRouter()

@router.post("/", response_model=Contact)
async def create_contact(
    contact: ContactCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new contact message and notify admin"""
    # FIXED: Use database model (DBContact), not API schema (Contact)
    db_contact = DBContact(
        name=contact.name,
        email=contact.email,
        message=contact.message
    )
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)

    # Send Notification Email to Admin
    subject = f"New Message: {contact.name}"
    html_content = f"""
    <div style="font-family: sans-serif; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
        <h2 style="color: #333; margin-top: 0;">New Contact Message</h2>
        <p><strong>Name:</strong> {contact.name}</p>
        <p><strong>Email:</strong> {contact.email}</p>
        <p><strong>Message:</strong></p>
        <div style="background: #f9f9f9; padding: 15px; border-left: 4px solid #007bff; margin: 10px 0;">
            {contact.message}
        </div>
    </div>
    """
    
    # Send to the configured sender email (admin)
    if settings.sender_email:
        settings_rows = db.execute(text("SELECT key, value FROM system_settings")).all()
        db_settings = {s[0]: s[1] for s in settings_rows}
        site_name = db_settings.get("site_name", "Admin")

        await email_service.send_email_background(
            background_tasks,
            to_email=settings.sender_email,
            subject=subject,
            html_content=html_content,
            to_name=f"{site_name} Admin",
            reply_to={"email": contact.email, "name": contact.name}
        )

    return db_contact

@router.get("/", response_model=list[Contact])
async def get_contacts(
    skip: int = 0,
    limit: int = 100,
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all contact messages (admin only)"""
    contacts = db.query(DBContact).offset(skip).limit(limit).all()
    return contacts

@router.get("/{contact_id}", response_model=Contact)
async def get_contact(
    contact_id: int,
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific contact message"""
    contact = db.query(DBContact).filter(DBContact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.put("/{contact_id}/read")
async def mark_contact_read(
    contact_id: int,
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark contact as read"""
    contact = db.query(DBContact).filter(DBContact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    contact.is_read = True
    db.commit()
    return {"message": "Contact marked as read"}

@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: int,
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a contact message"""
    contact = db.query(DBContact).filter(DBContact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    db.delete(contact)
    db.commit()
    return {"message": "Contact deleted"}