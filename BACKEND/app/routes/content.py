from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, Request
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from pathlib import Path
import logging

from database import get_db
from services.content_service import ContentService
from schemas.blog import (
    BlogPostCreate, BlogPost, ContentRevision, ContentWorkflow,
    SEOMetadata, ContentTemplate, ContentAnalytics, BulkOperation,
    SEOAnalysisResponse, ContentScheduleRequest, ContentScheduleResponse,
    MediaFile, ContentWorkflowUpdate, BulkOperationCreate, BulkOperationStatus
)

router = APIRouter()

# Content Management APIs

@router.post("/posts", response_model=BlogPost)
async def create_post(
    post: BlogPostCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new blog post with workflow management"""
    try:
        content_service = ContentService(db)
        author = request.headers.get("X-User", "admin")  # Would be set by auth middleware
        created_post = content_service.create_post_with_workflow(post, author)
        return created_post
    except Exception as e:
        raise HTTPException(500, f"Failed to create post: {str(e)}")

@router.put("/posts/{post_id}", response_model=BlogPost)
async def update_post(
    post_id: int,
    post_data: dict,
    request: Request,
    db: Session = Depends(get_db)
):
    """Update a blog post with revision tracking"""
    try:
        content_service = ContentService(db)
        author = request.headers.get("X-User", "admin")
        updated_post = content_service.update_post_with_revision(post_id, post_data, author)
        return updated_post
    except Exception as e:
        raise HTTPException(500, f"Failed to update post: {str(e)}")

@router.post("/schedule", response_model=ContentScheduleResponse)
async def schedule_post(
    schedule_data: ContentScheduleRequest,
    db: Session = Depends(get_db)
):
    """Schedule a post for publication"""
    try:
        content_service = ContentService(db)
        result = content_service.schedule_post(schedule_data)
        return result
    except Exception as e:
        raise HTTPException(500, f"Failed to schedule post: {str(e)}")

@router.post("/media/upload")
async def upload_media(
    file: UploadFile = File(...),
    alt_text: Optional[str] = Form(None),
    caption: Optional[str] = Form(None),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Upload media files"""
    try:
        content_service = ContentService(db)
        uploaded_by = getattr(request, 'user', 'admin') if request else 'admin'

        result = content_service.upload_media(
            file=file,
            alt_text=alt_text,
            caption=caption,
            uploaded_by=uploaded_by
        )
        return result
    except Exception as e:
        raise HTTPException(500, f"Failed to upload media: {str(e)}")

@router.get("/media")
async def get_media_files(
    file_type: Optional[str] = None,
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    """Get list of uploaded media files with stats and folder structure"""
    logger = logging.getLogger(__name__)

    try:
        from models.blog import MediaFile as MediaFileModel
        from datetime import datetime, timedelta
        from sqlalchemy import func

        # Check if MediaFileModel exists
        try:
            from models.blog import MediaFile
        except ImportError as e:
            logger.error(f"🐛 MEDIA API: Failed to import MediaFile model: {e}")
            raise HTTPException(500, f"MediaFile model import failed: {e}")

        query = db.query(MediaFileModel)

        if file_type:
            query = query.filter(MediaFileModel.file_type == file_type)

        media_files = query.order_by(MediaFileModel.created_at.desc()).offset(offset).limit(limit).all()

        # Calculate stats with detailed logging
        total_files = db.query(func.count(MediaFileModel.id)).scalar() or 0

        recent_files = db.query(func.count(MediaFileModel.id)).filter(
            MediaFileModel.created_at >= datetime.now() - timedelta(days=7)
        ).scalar() or 0

        # Mock folder structure (in real implementation, you'd have a folder model)
        folder_structure = [
            {"id": "images", "name": "Images", "count": len([f for f in media_files if f.file_type and f.file_type.startswith('image/')])},
            {"id": "videos", "name": "Videos", "count": len([f for f in media_files if f.file_type and f.file_type.startswith('video/')])},
            {"id": "documents", "name": "Documents", "count": len([f for f in media_files if f.file_type and 'document' in f.file_type])},
            {"id": "audio", "name": "Audio", "count": len([f for f in media_files if f.file_type and f.file_type.startswith('audio/')])},
            {"id": "archives", "name": "Archives", "count": len([f for f in media_files if f.file_type and 'zip' in f.file_type])}
        ]

        # Transform media files to match expected format
        transformed_media = []
        for file in media_files:
            try:
                transformed_file = {
                    "id": str(file.id),
                    "name": file.filename or "Unknown File",
                    "url": f"/media/files/{file.id}",  # URL to access the file
                    "type": file.file_type or "unknown",
                    "size": file.file_size or 0,
                    "uploadedAt": file.created_at.isoformat() if file.created_at else datetime.now().isoformat(),
                    "folderId": "all",  # Default folder assignment
                    "dimensions": "N/A",  # Would need image processing to get real dimensions
                    "altText": file.alt_text or "",
                    "caption": file.caption or ""
                }
                transformed_media.append(transformed_file)
            except Exception as e:
                logger.error(f"🐛 MEDIA API: Error transforming file {file.id}: {e}")

        response_data = {
            "media": transformed_media,
            "stats": {
                "totalFiles": total_files,
                "totalFolders": len(folder_structure),
                "recentFiles": recent_files
            },
            "folders": folder_structure
        }

        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"🐛 MEDIA API: Exception occurred: {type(e).__name__}: {str(e)}")
        logger.error(f"🐛 MEDIA API: Exception details: {e.__dict__ if hasattr(e, '__dict__') else 'No details'}")
        import traceback
        logger.error(f"🐛 MEDIA API: Traceback: {traceback.format_exc()}")
        raise HTTPException(500, f"Failed to get media files: {str(e)}")

@router.delete("/media/{file_id}")
async def delete_media_file(
    file_id: int,
    db: Session = Depends(get_db)
):
    """Delete a media file"""
    try:
        from models.blog import MediaFile as MediaFileModel

        media_file = db.query(MediaFileModel).filter(MediaFileModel.id == file_id).first()
        if not media_file:
            raise HTTPException(404, "Media file not found")

        # Delete physical file
        file_path = Path(media_file.file_path)
        if file_path.exists():
            file_path.unlink()

        # Delete database record
        db.delete(media_file)
        db.commit()

        return {"message": "Media file deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Failed to delete media file: {str(e)}")

@router.get("/seo/analyze/{post_id}", response_model=SEOAnalysisResponse)
async def analyze_seo(
    post_id: int,
    content: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Analyze post content for SEO optimization"""
    try:
        content_service = ContentService(db)
        analysis = content_service.analyze_seo(post_id, content)
        return analysis
    except Exception as e:
        raise HTTPException(500, f"Failed to analyze SEO: {str(e)}")

@router.put("/seo/{post_id}")
async def update_seo_metadata(
    post_id: int,
    seo_data: dict,
    db: Session = Depends(get_db)
):
    """Update SEO metadata for a post"""
    try:
        from models.blog import SEOMetadata

        seo_meta = db.query(SEOMetadata).filter(SEOMetadata.post_id == post_id).first()

        if not seo_meta:
            seo_meta = SEOMetadata(post_id=post_id, **seo_data)
            db.add(seo_meta)
        else:
            for key, value in seo_data.items():
                if hasattr(seo_meta, key):
                    setattr(seo_meta, key, value)

        db.commit()
        db.refresh(seo_meta)

        return {"message": "SEO metadata updated successfully", "seo_id": seo_meta.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Failed to update SEO metadata: {str(e)}")

@router.get("/seo/{post_id}")
async def get_seo_metadata(
    post_id: int,
    db: Session = Depends(get_db)
):
    """Get SEO metadata for a post"""
    try:
        from models.blog import SEOMetadata

        seo_meta = db.query(SEOMetadata).filter(SEOMetadata.post_id == post_id).first()
        if not seo_meta:
            raise HTTPException(404, "SEO metadata not found")

        return {
            "post_id": seo_meta.post_id,
            "meta_title": seo_meta.meta_title,
            "meta_description": seo_meta.meta_description,
            "meta_keywords": seo_meta.meta_keywords,
            "canonical_url": seo_meta.canonical_url,
            "og_title": seo_meta.og_title,
            "og_description": seo_meta.og_description,
            "og_image": seo_meta.og_image,
            "twitter_card": seo_meta.twitter_card,
            "focus_keyword": seo_meta.focus_keyword,
            "readability_score": seo_meta.readability_score,
            "seo_score": seo_meta.seo_score
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to get SEO metadata: {str(e)}")

# Workflow Management APIs

@router.get("/workflow/{post_id}", response_model=ContentWorkflow)
async def get_workflow(
    post_id: int,
    db: Session = Depends(get_db)
):
    """Get workflow status for a post"""
    try:
        from models.blog import ContentWorkflow

        workflow = db.query(ContentWorkflow).filter(ContentWorkflow.post_id == post_id).first()
        if not workflow:
            raise HTTPException(404, "Workflow not found")

        return workflow
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to get workflow: {str(e)}")

@router.put("/workflow/{post_id}", response_model=ContentWorkflow)
async def update_workflow(
    post_id: int,
    workflow_data: ContentWorkflowUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Update workflow status for a post"""
    try:
        content_service = ContentService(db)
        updated_by = request.headers.get("X-User", "admin")

        workflow_dict = workflow_data.dict(exclude_unset=True)
        workflow = content_service.update_workflow(post_id, workflow_dict, updated_by)

        return workflow
    except Exception as e:
        raise HTTPException(500, f"Failed to update workflow: {str(e)}")

@router.post("/workflow/{post_id}/approve")
async def approve_content(
    post_id: int,
    approval_notes: Optional[str] = None,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Approve content for publication"""
    try:
        from models.blog import ContentWorkflow, BlogPost

        workflow = db.query(ContentWorkflow).filter(ContentWorkflow.post_id == post_id).first()
        if not workflow:
            raise HTTPException(404, "Workflow not found")

        # Update workflow
        workflow.status = "approved"
        workflow.approval_notes = approval_notes or "Approved for publication"

        # Update post status
        post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
        if post:
            post.published_at = datetime.now()
            

        db.commit()

        return {"message": "Content approved and published", "post_id": post_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Failed to approve content: {str(e)}")

# Revision Management APIs

@router.get("/revisions/{post_id}", response_model=List[ContentRevision])
async def get_revisions(
    post_id: int,
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db)
):
    """Get revision history for a post"""
    try:
        from models.blog import ContentRevision

        revisions = db.query(ContentRevision).filter(
            ContentRevision.post_id == post_id
        ).order_by(ContentRevision.revision_number.desc()).limit(limit).all()

        return revisions
    except Exception as e:
        raise HTTPException(500, f"Failed to get revisions: {str(e)}")

@router.post("/revisions/{post_id}")
async def create_revision(
    post_id: int,
    revision_data: dict,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new revision for a post"""
    try:
        from models.blog import ContentRevision

        # Get latest revision number
        latest = db.query(ContentRevision).filter(
            ContentRevision.post_id == post_id
        ).order_by(ContentRevision.revision_number.desc()).first()

        revision_number = (latest.revision_number + 1) if latest else 1

        revision = ContentRevision(
            post_id=post_id,
            revision_number=revision_number,
            revised_by=request.headers.get("X-User", "admin"),
            **revision_data
        )

        db.add(revision)
        db.commit()
        db.refresh(revision)

        return {"message": "Revision created", "revision_id": revision.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Failed to create revision: {str(e)}")

@router.put("/revisions/{revision_id}/restore")
async def restore_revision(
    revision_id: int,
    db: Session = Depends(get_db)
):
    """Restore a post to a previous revision"""
    try:
        from models.blog import ContentRevision, BlogPost

        revision = db.query(ContentRevision).filter(ContentRevision.id == revision_id).first()
        if not revision:
            raise HTTPException(404, "Revision not found")

        post = db.query(BlogPost).filter(BlogPost.id == revision.post_id).first()
        if not post:
            raise HTTPException(404, "Post not found")

        # Update post with revision data
        post.title = revision.title or post.title
        post.content = revision.content or post.content
        post.excerpt = revision.excerpt or post.excerpt
        post.tags = revision.tags or post.tags
        post.section = revision.section or post.section
        post.featured_image = revision.featured_image or post.featured_image

        db.commit()

        return {"message": "Revision restored successfully", "post_id": post.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Failed to restore revision: {str(e)}")

# Bulk Operations APIs

@router.post("/bulk", response_model=BulkOperation)
async def execute_bulk_operation(
    operation: BulkOperationCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Execute bulk content operations"""
    try:
        content_service = ContentService(db)
        initiated_by = request.headers.get("X-User", "admin")

        bulk_op = content_service.bulk_operation(operation, initiated_by)
        return bulk_op
    except Exception as e:
        raise HTTPException(500, f"Failed to execute bulk operation: {str(e)}")

@router.get("/bulk/{operation_id}", response_model=BulkOperationStatus)
async def get_bulk_operation_status(
    operation_id: int,
    db: Session = Depends(get_db)
):
    """Get status of a bulk operation"""
    try:
        from models.blog import BulkOperation

        operation = db.query(BulkOperation).filter(BulkOperation.id == operation_id).first()
        if not operation:
            raise HTTPException(404, "Bulk operation not found")

        # Calculate progress
        total_count = len(operation.affected_posts)
        completed_count = 0  # In a real implementation, you'd track this

        return BulkOperationStatus(
            operation_id=operation.id,
            status=operation.status,
            progress=completed_count / total_count if total_count > 0 else 0,
            completed_count=completed_count,
            total_count=total_count,
            errors=operation.error_message.split('\n') if operation.error_message else None
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to get bulk operation status: {str(e)}")

# Content Templates APIs

@router.get("/templates", response_model=List[ContentTemplate])
async def get_content_templates(
    template_type: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get available content templates"""
    try:
        from models.blog import ContentTemplate

        query = db.query(ContentTemplate)

        if template_type:
            query = query.filter(ContentTemplate.template_type == template_type)

        if active_only:
            query = query.filter(ContentTemplate.is_active == True)

        templates = query.order_by(ContentTemplate.name).all()
        return templates
    except Exception as e:
        raise HTTPException(500, f"Failed to get templates: {str(e)}")

@router.post("/templates", response_model=ContentTemplate)
async def create_content_template(
    template: ContentTemplate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new content template"""
    try:
        from models.blog import ContentTemplate

        template.created_by = request.headers.get("X-User", "admin")
        db_template = ContentTemplate(**template.dict())
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        return db_template
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Failed to create template: {str(e)}")

@router.put("/templates/{template_id}/use")
async def increment_template_usage(
    template_id: int,
    db: Session = Depends(get_db)
):
    """Increment template usage count"""
    try:
        from models.blog import ContentTemplate

        template = db.query(ContentTemplate).filter(ContentTemplate.id == template_id).first()
        if not template:
            raise HTTPException(404, "Template not found")

        template.usage_count += 1
        db.commit()

        return {"message": "Template usage updated"}
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Failed to update template usage: {str(e)}")

# Content Analytics APIs

@router.get("/analytics/content")
async def get_content_analytics(
    post_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get detailed content performance analytics"""
    try:
        content_service = ContentService(db)

        # Parse dates
        parsed_date_from = datetime.fromisoformat(date_from) if date_from else None
        parsed_date_to = datetime.fromisoformat(date_to) if date_to else None

        analytics = content_service.get_content_analytics(
            post_id=post_id,
            date_from=parsed_date_from,
            date_to=parsed_date_to
        )

        return {"analytics": analytics}
    except Exception as e:
        raise HTTPException(500, f"Failed to get content analytics: {str(e)}")

@router.get("/analytics/performance")
async def get_content_performance(
    timeframe_days: int = Query(30, description="Days to analyze"),
    limit: int = Query(20, description="Number of posts to return"),
    db: Session = Depends(get_db)
):
    """Get content performance metrics"""
    try:
        from models.blog import BlogPost
        from sqlalchemy import func

        start_date = datetime.now() - timedelta(days=timeframe_days)

        # Get top performing content
        performance_data = db.query(
            BlogPost.id,
            BlogPost.title,
            BlogPost.view_count,
            BlogPost.like_count,
            BlogPost.comment_count,
            func.coalesce(BlogPost.share_count, 0).label('share_count'),
            BlogPost.published_at
        ).filter(
            BlogPost.published_at >= start_date
        ).order_by(
            (BlogPost.view_count + BlogPost.like_count * 2 + func.coalesce(BlogPost.share_count, 0) * 3).desc()
        ).limit(limit).all()

        return {
            "timeframe_days": timeframe_days,
            "performance_data": [
                {
                    "post_id": row.id,
                    "title": row.title,
                    "views": row.view_count,
                    "likes": row.like_count,
                    "comments": row.comment_count,
                    "shares": row.share_count,
                    "engagement_score": row.view_count + row.like_count * 2 + row.share_count * 3,
                    "published_at": row.published_at.isoformat() if row.published_at else None
                }
                for row in performance_data
            ]
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to get content performance: {str(e)}")

# Dashboard APIs

@router.get("/dashboard/overview")
async def get_content_dashboard(
    db: Session = Depends(get_db)
):
    """Get content management dashboard overview"""
    try:
        from models.blog import BlogPost, ContentWorkflow, MediaFile

        # Basic stats
        total_posts = db.query(func.count(BlogPost.id)).scalar() or 0
        published_posts = db.query(func.count(BlogPost.id)).filter(BlogPost.published_at.isnot(None)).scalar() or 0
        draft_posts = total_posts - published_posts

        # Workflow stats
        workflow_stats = db.query(
            ContentWorkflow.status,
            func.count(ContentWorkflow.id)
        ).group_by(ContentWorkflow.status).all()

        workflow_counts = {status: count for status, count in workflow_stats}

        # Recent activity
        recent_posts = db.query(BlogPost).order_by(BlogPost.created_at.desc()).limit(5).all()

        # Media stats
        total_media = db.query(func.count(MediaFile.id)).scalar() or 0
        media_by_type = db.query(
            MediaFile.file_type,
            func.count(MediaFile.id)
        ).group_by(MediaFile.file_type).all()

        return {
            "overview": {
                "total_posts": total_posts,
                "published_posts": published_posts,
                "draft_posts": draft_posts,
                "total_media": total_media
            },
            "workflow": {
                "draft": workflow_counts.get("draft", 0),
                "review": workflow_counts.get("review", 0),
                "approved": workflow_counts.get("approved", 0),
                "published": workflow_counts.get("published", 0)
            },
            "media_types": {media_type: count for media_type, count in media_by_type},
            "recent_posts": [
                {
                    "id": post.id,
                    "title": post.title,
                    "status": "published" if post.published_at else "draft",
                    "created_at": post.created_at.isoformat()
                }
                for post in recent_posts
            ]
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to get dashboard data: {str(e)}")

@router.get("/dashboard/workflow")
async def get_workflow_dashboard(
    status: Optional[str] = None,
    assigned_to: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db)
):
    """Get workflow management dashboard"""
    try:
        from models.blog import ContentWorkflow, BlogPost

        query = db.query(ContentWorkflow).join(BlogPost)

        if status:
            query = query.filter(ContentWorkflow.status == status)

        if assigned_to:
            query = query.filter(ContentWorkflow.assigned_to == assigned_to)

        workflows = query.order_by(ContentWorkflow.created_at.desc()).limit(limit).all()

        return {
            "workflows": [
                {
                    "id": wf.id,
                    "post_id": wf.post_id,
                    "post_title": wf.post.title if wf.post else "Unknown",
                    "status": wf.status,
                    "priority": wf.priority,
                    "assigned_to": wf.assigned_to,
                    "due_date": wf.due_date.isoformat() if wf.due_date else None,
                    "created_at": wf.created_at.isoformat(),
                    "updated_at": wf.updated_at.isoformat()
                }
                for wf in workflows
            ]
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to get workflow dashboard: {str(e)}")