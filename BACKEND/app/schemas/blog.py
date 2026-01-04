from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime

class BlogPostBase(BaseModel):
    title: str
    content: Optional[str] = None
    excerpt: Optional[str] = None
    template_type: Optional[str] = None
    featured_image: Optional[str] = None
    video_url: Optional[str] = None
    tags: Optional[List[str]] = None
    section: Optional[str] = 'others'
    slug: Optional[str] = None
    priority: Optional[int] = 0
    is_featured: Optional[bool] = False

class BlogPostCreate(BlogPostBase):
    pass

class BlogPost(BlogPostBase):
    id: int
    published_at: Optional[datetime] = None
    view_count: int
    like_count: int
    comment_count: int
    share_count: int

    class Config:
        from_attributes = True

class BlogPostSearchResult(BlogPost):
    search_score: Optional[float] = None
    matched_terms: Optional[List[str]] = None

class SearchFilters(BaseModel):
    sections: List[str] = ['latest', 'popular', 'others', 'featured']
    tags: List[str] = ['ai', 'startup', 'innovation', 'opinions', 'business', 'software']

class SearchRequest(BaseModel):
    query: str = ""
    section: Optional[str] = None
    tags: Optional[List[str]] = None
    sort: Optional[str] = "relevance"  # relevance, recent, popular
    offset: Optional[int] = 0
    limit: Optional[int] = 20

class SearchResponse(BaseModel):
    results: List[BlogPostSearchResult]
    total: int
    query: str
    filters_applied: dict
    search_time: float

class SearchSuggestions(BaseModel):
    suggestions: List[str]
    popular: List[str]
    trending: List[str]

class SearchAnalyticsCreate(BaseModel):
    query: str
    results_count: int
    filters_used: dict
    user_identifier: str
    user_agent: Optional[str] = None

# Newsletter Schemas
class NewsletterSubscriberBase(BaseModel):
    name: str
    email: str
    preferences: Optional[dict] = None

class NewsletterSubscriberCreate(NewsletterSubscriberBase):
    pass

class NewsletterSubscriber(NewsletterSubscriberBase):
    id: int
    subscribed_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

class NewsletterSegmentBase(BaseModel):
    name: str
    type: Optional[str] = "dynamic"
    criteria: dict
    description: Optional[str] = None

class NewsletterSegmentCreate(NewsletterSegmentBase):
    pass

class NewsletterSegment(NewsletterSegmentBase):
    id: int
    cached_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class NewsletterCampaignBase(BaseModel):
    subject: str
    content: str
    template_type: Optional[str] = "weekly"

class NewsletterCampaignCreate(NewsletterCampaignBase):
    scheduled_at: Optional[datetime] = None
    segment_id: Optional[int] = None
    status: Optional[str] = "draft"

class NewsletterCampaign(NewsletterCampaignBase):
    id: int
    status: str  # draft, scheduled, sent, failed
    scheduled_at: Optional[datetime]
    sent_at: Optional[datetime]
    recipient_count: int
    created_at: datetime

    class Config:
        from_attributes = True

class NewsletterTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    subject_template: str
    content_template: str
    category: Optional[str] = None
    thumbnail_url: Optional[str] = None

class NewsletterTemplateCreate(NewsletterTemplateBase):
    pass

class NewsletterTemplate(NewsletterTemplateBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    author_name: str
    author_email: Optional[str] = None
    content: str
    parent_id: Optional[int] = None

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    blog_post_id: int
    is_approved: bool
    created_at: datetime

    class Config:
        from_attributes = True

class TemporalUserBase(BaseModel):
    fingerprint: str
    name: str
    email: Optional[str] = None
    device_info: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class TemporalUserCreate(TemporalUserBase):
    pass

class TemporalUser(TemporalUserBase):
    id: int
    created_at: datetime
    last_seen: datetime
    expires_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

class LikeCreate(BaseModel):
    fingerprint: Optional[str] = None  # Primary field for device fingerprint
    user_identifier: Optional[str] = None  # Legacy field for backward compatibility
    
    def __init__(self, **data):
        # If fingerprint is not provided, use user_identifier as fallback
        if 'fingerprint' not in data or data['fingerprint'] is None:
            if 'user_identifier' in data and data['user_identifier'] is not None:
                data['fingerprint'] = data['user_identifier']
        super().__init__(**data)
    
    @validator('fingerprint')
    def validate_fingerprint(cls, v, values):
        # Ensure we have either fingerprint or user_identifier
        if v is None and values.get('user_identifier') is None:
            raise ValueError('Either fingerprint or user_identifier is required')
        return v

class Like(BaseModel):
    id: int
    blog_post_id: int
    fingerprint: str
    user_identifier: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ViewCreate(BaseModel):
    fingerprint: str

# Analytics Schemas
class PageViewAnalyticsBase(BaseModel):
    post_id: Optional[int] = None
    session_id: str
    user_identifier: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    device_type: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    screen_resolution: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    timezone: Optional[str] = None
    referrer: Optional[str] = None
    referrer_domain: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    page_url: Optional[str] = None
    time_on_page: Optional[int] = None
    scroll_depth: Optional[float] = None

class PageViewAnalyticsCreate(PageViewAnalyticsBase):
    pass

class PageViewAnalytics(PageViewAnalyticsBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class ContentEngagementAnalyticsBase(BaseModel):
    post_id: Optional[int] = None
    session_id: str
    user_identifier: Optional[str] = None
    action_type: str
    element_type: Optional[str] = None
    element_id: Optional[str] = None
    element_text: Optional[str] = None
    page_url: Optional[str] = None
    section_visible: Optional[str] = None
    time_on_page: Optional[int] = None
    action_metadata: Optional[dict] = None

class ContentEngagementAnalyticsCreate(ContentEngagementAnalyticsBase):
    pass

class ContentEngagementAnalytics(ContentEngagementAnalyticsBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class UserSessionAnalyticsBase(BaseModel):
    session_id: str
    user_identifier: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[int] = None
    page_views: int = 0
    unique_pages: int = 0
    actions_taken: int = 0
    device_type: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    is_bounce: bool = False
    has_search: bool = False
    has_newsletter_signup: bool = False
    has_social_share: bool = False
    entry_page: Optional[str] = None
    exit_page: Optional[str] = None

class UserSessionAnalyticsCreate(UserSessionAnalyticsBase):
    pass

class UserSessionAnalytics(UserSessionAnalyticsBase):
    id: int

    class Config:
        from_attributes = True

class ReferralAnalyticsBase(BaseModel):
    session_id: str
    referrer_url: Optional[str] = None
    referrer_domain: Optional[str] = None
    referrer_type: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_term: Optional[str] = None
    utm_content: Optional[str] = None
    landing_page: Optional[str] = None
    landing_page_title: Optional[str] = None
    converted: bool = False
    conversion_type: Optional[str] = None
    conversion_value: float = 0

class ReferralAnalyticsCreate(ReferralAnalyticsBase):
    pass

class ReferralAnalytics(ReferralAnalyticsBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class AnalyticsDashboardResponse(BaseModel):
    total_views: int
    total_sessions: int
    total_users: int
    active_users: int
    page_views_today: int
    page_views_yesterday: int
    top_content: List[dict]
    popular_searches: List[dict]
    device_breakdown: dict
    geographic_data: List[dict]
    referral_sources: List[dict]
    real_time_metrics: dict

class AnalyticsReportRequest(BaseModel):
    report_type: str  # daily, weekly, monthly, custom
    date_range_start: datetime
    date_range_end: datetime
    include_charts: bool = True
    export_format: Optional[str] = None  # pdf, csv, excel

# Content Management Schemas
class MediaFileBase(BaseModel):
    filename: str
    original_filename: str
    file_path: str
    file_url: str
    file_type: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    dimensions: Optional[str] = None
    alt_text: Optional[str] = None
    caption: Optional[str] = None
    is_featured: Optional[bool] = False

class MediaFileCreate(MediaFileBase):
    pass

class MediaFile(MediaFileBase):
    id: int
    uploaded_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ContentRevisionBase(BaseModel):
    revision_number: int
    title: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None
    tags: Optional[List[str]] = None
    section: Optional[str] = None
    featured_image: Optional[str] = None
    revision_note: Optional[str] = None

class ContentRevisionCreate(ContentRevisionBase):
    pass

class ContentRevision(ContentRevisionBase):
    id: int
    post_id: int
    revised_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ContentWorkflowBase(BaseModel):
    status: str
    priority: Optional[str] = "medium"
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    review_notes: Optional[str] = None
    approval_notes: Optional[str] = None

class ContentWorkflowCreate(ContentWorkflowBase):
    pass

class ContentWorkflow(ContentWorkflowBase):
    id: int
    post_id: int
    assigned_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SEOMetadataBase(BaseModel):
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    canonical_url: Optional[str] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None
    twitter_card: Optional[str] = "summary_large_image"
    focus_keyword: Optional[str] = None

class SEOMetadataCreate(SEOMetadataBase):
    pass

class SEOMetadata(SEOMetadataBase):
    id: int
    post_id: int
    readability_score: Optional[float] = None
    seo_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ContentTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    template_type: str
    content_structure: Optional[dict] = None
    default_tags: Optional[List[str]] = None
    default_section: Optional[str] = None
    is_active: Optional[bool] = True

class ContentTemplateCreate(ContentTemplateBase):
    pass

class ContentTemplate(ContentTemplateBase):
    id: int
    usage_count: int
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ContentAnalyticsBase(BaseModel):
    metric_type: str
    metric_value: float
    device_type: Optional[str] = None
    referrer_type: Optional[str] = None
    country: Optional[str] = None
    source_url: Optional[str] = None

class ContentAnalyticsCreate(ContentAnalyticsBase):
    pass

class ContentAnalytics(ContentAnalyticsBase):
    id: int
    post_id: Optional[int] = None
    date: datetime

    class Config:
        from_attributes = True

class BulkOperationBase(BaseModel):
    operation_type: str
    operation_data: dict
    affected_posts: List[int]

class BulkOperationCreate(BulkOperationBase):
    pass

class BulkOperation(BulkOperationBase):
    id: int
    status: str
    initiated_by: Optional[str] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Content Management API Schemas
class ContentScheduleRequest(BaseModel):
    post_id: int
    publish_at: datetime
    timezone: Optional[str] = "UTC"

class ContentScheduleResponse(BaseModel):
    success: bool
    post_id: int
    scheduled_at: datetime
    message: str

class SEOAnalysisRequest(BaseModel):
    post_id: int
    content: Optional[str] = None

class SEOAnalysisResponse(BaseModel):
    post_id: int
    readability_score: float
    seo_score: float
    suggestions: List[dict]
    keyword_analysis: dict
    recommendations: List[str]

class MediaUploadResponse(BaseModel):
    success: bool
    file_id: int
    file_url: str
    filename: str
    file_size: int
    message: str

class ContentWorkflowUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    review_notes: Optional[str] = None
    approval_notes: Optional[str] = None

class BulkOperationStatus(BaseModel):
    operation_id: int
    status: str
    progress: Optional[float] = None
    completed_count: Optional[int] = None
    total_count: Optional[int] = None
    errors: Optional[List[str]] = None