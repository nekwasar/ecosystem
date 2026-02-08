import os
import shutil
import uuid
from typing import List, Optional
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc

from database import get_db
from models.media import FileAsset, RouteType
from core.config import settings

# --- Conf ---
UPLOAD_DIR = Path("BACKEND/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# --- Routers ---
router = APIRouter() # Admin
public_router = APIRouter() # Share/Public

# --- Helpers ---
def get_file_path(filename: str) -> Path:
    return UPLOAD_DIR / filename

def get_unique_slug(db: Session, base_slug: str) -> str:
    # Simple check, in production iterate to find unique
    exists = db.query(FileAsset).filter(FileAsset.custom_slug == base_slug).first()
    if exists:
        return f"{base_slug}-{uuid.uuid4().hex[:4]}"
    return base_slug

# --- Admin Routes ---

@router.get("", response_model=List[dict]) 
async def list_assets(
    limit: int = 50, 
    offset: int = 0, 
    type_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(FileAsset)
    if type_filter:
         if type_filter == 'image':
             query = query.filter(FileAsset.mime_type.like("image/%"))
         elif type_filter == 'video':
             query = query.filter(FileAsset.mime_type.like("video/%"))
         else:
             query = query.filter(FileAsset.mime_type.like(f"%{type_filter}%"))
             
    assets = query.order_by(desc(FileAsset.created_at)).offset(offset).limit(limit).all()
    
    # Return valid JSON
    return [
        {
            "id": a.id,
            "filename": a.filename,
            "original_name": a.original_name,
            "mime_type": a.mime_type,
            "slug": a.custom_slug,
            "file_url": f"/share/{a.custom_slug}" if a.route_type == RouteType.SHARE else f"https://cdn.nekwasar.com/{a.custom_slug}",
            "route_type": a.route_type,
            "size": a.size_bytes,
            "created_at": a.created_at.isoformat()
        }
        for a in assets
    ]

@router.post("/upload")
async def upload_asset(
    file: UploadFile = File(...),
    slug: str = Form(...),
    route_type: str = Form("SHARE"), # CDN or SHARE
    db: Session = Depends(get_db)
):
    # 1. Validate Slug
    final_slug = get_unique_slug(db, slug)
    
    # 2. Save File
    file_ext = os.path.splitext(file.filename)[1]
    safe_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = get_file_path(safe_filename)
    
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        file_size = os.path.getsize(file_path)
    except Exception as e:
        raise HTTPException(500, f"File save failed: {str(e)}")
        
    # 3. Create DB Record
    new_asset = FileAsset(
        filename=safe_filename,
        original_name=file.filename,
        mime_type=file.content_type,
        size_bytes=file_size,
        route_type=RouteType(route_type),
        custom_slug=final_slug
    )
    db.add(new_asset)
    db.commit()
    db.refresh(new_asset)
    
    return {
        "success": True,
        "slug": final_slug,
        "url": f"/share/{final_slug}" if route_type == "SHARE" else f"https://cdn.nekwasar.com/{final_slug}"
    }

@router.delete("/{id}")
async def delete_asset(id: int, db: Session = Depends(get_db)):
    asset = db.query(FileAsset).filter(FileAsset.id == id).first()
    if not asset:
        raise HTTPException(404, "Asset not found")
        
    # Delete from disk
    file_path = get_file_path(asset.filename)
    if file_path.exists():
        os.remove(file_path)
        
    db.delete(asset)
    db.commit()
    return {"success": True}

# --- Public Routes (Share / Download) ---

@public_router.get("/share/{slug}")
async def view_shared_asset(slug: str, db: Session = Depends(get_db)):
    asset = db.query(FileAsset).filter(
        FileAsset.custom_slug == slug, 
        FileAsset.route_type == RouteType.SHARE
    ).first()
    
    if not asset:
        raise HTTPException(404)
        
    file_path = get_file_path(asset.filename)
    if not file_path.exists():
        raise HTTPException(404, "File missing on server")
        
    return FileResponse(file_path, media_type=asset.mime_type)

@public_router.get("/d/{slug}")
async def download_shared_asset(slug: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    asset = db.query(FileAsset).filter(
        FileAsset.custom_slug == slug
        # Note: We allow downloading CDN assets via this route too if user guesses it? 
        # Or strict? strict implies: FileAsset.route_type == RouteType.SHARE
    ).first()
    
    if not asset:
        raise HTTPException(404)

    file_path = get_file_path(asset.filename)
    if not file_path.exists():
        raise HTTPException(404, "File missing")

    # Increment Count
    asset.download_count += 1
    db.commit()

    return FileResponse(
        file_path, 
        media_type=asset.mime_type, 
        filename=asset.original_name, # Force download name
        headers={"Content-Disposition": f"attachment; filename={asset.original_name}"}
    )

# --- CDN Helper (Called from main.py) ---
async def serve_cdn_asset(slug: str, download: bool, db: Session):
    asset = db.query(FileAsset).filter(
        FileAsset.custom_slug == slug,
        FileAsset.route_type == RouteType.CDN
    ).first()
    
    if not asset:
        return None # Let caller 404
        
    file_path = get_file_path(asset.filename)
    if not file_path.exists():
        return None
        
    if download:
        asset.download_count += 1
        db.commit()
        return FileResponse(
            file_path, 
            media_type=asset.mime_type, 
            filename=asset.original_name,
            headers={"Content-Disposition": f"attachment; filename={asset.original_name}"}
        )
    else:
        return FileResponse(file_path, media_type=asset.mime_type)
