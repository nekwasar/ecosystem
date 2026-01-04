from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./nekwasa.db"

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 120  # 2 hours

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # CORS
    allowed_origins: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://nekwasar.com",
        "https://blog.nekwasar.com",
        "https://store.nekwasar.com"
    ]

    # File Upload
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    upload_directory: str = "uploads"

    # Email (newsletter system)
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    from_email: Optional[str] = None
    from_name: Optional[str] = None
    
    # Brevo (Sendinblue)
    brevo_api_key: Optional[str] = None
    sender_email: Optional[str] = None
    sender_name: Optional[str] = None

    # Analytics
    google_analytics_property_id: Optional[str] = None

    # Payment
    stripe_secret_key: Optional[str] = None
    stripe_publishable_key: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Allow extra environment variables without crashing

# Global settings instance
settings = Settings()