import os
import uuid
import hashlib
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import httpx
import aiofiles

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bunny.net configuration
BUNNY_API_KEY = os.getenv("BUNNY_API_KEY", "")
BUNNY_STORAGE_ZONE = os.getenv("BUNNY_STORAGE_ZONE", "")
BUNNY_HOSTNAME = os.getenv("BUNNY_HOSTNAME", "storage.bunnycdn.com")
CDN_BASE_URL = os.getenv("CDN_BASE_URL", "https://cdn.nekwasar.com")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting CDN Service with Bunny.net...")
    logger.info(f"Bunny Storage Zone: {BUNNY_STORAGE_ZONE}")
    logger.info(f"CDN URL: {CDN_BASE_URL}")
    yield
    logger.info("Shutting down CDN Service...")


app = FastAPI(title="CDN Service", description="Bunny.net CDN Integration", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


def generate_file_path(filename: str, folder: str = "uploads") -> str:
    """Generate unique file path"""
    ext = filename.split(".")[-1] if "." in filename else ""
    unique_name = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex
    return f"{folder}/{datetime.now().strftime('%Y/%m')}/{unique_name}"


async def upload_to_bunny(file_path: str, file_content: bytes) -> bool:
    """Upload file to Bunny.net Storage"""
    if not BUNNY_API_KEY or not BUNNY_STORAGE_ZONE:
        logger.warning("Bunny.net not configured, using local storage")
        return False
    
    url = f"https://{BUNNY_HOSTNAME}/{BUNNY_STORAGE_ZONE}/{file_path}"
    headers = {
        "AccessKey": BUNNY_API_KEY,
        "Content-Type": "application/octet-stream"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(url, content=file_content, headers=headers)
            if response.status_code == 201:
                logger.info(f"Uploaded to Bunny.net: {file_path}")
                return True
            else:
                logger.error(f"Bunny.net upload failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Bunny.net upload error: {e}")
            return False


async def delete_from_bunny(file_path: str) -> bool:
    """Delete file from Bunny.net Storage"""
    if not BUNNY_API_KEY or not BUNNY_STORAGE_ZONE:
        return False
    
    url = f"https://{BUNNY_HOSTNAME}/{BUNNY_STORAGE_ZONE}/{file_path}"
    headers = {"AccessKey": BUNNY_API_KEY}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(url, headers=headers)
            return response.status_code in [200, 204, 404]
        except Exception as e:
            logger.error(f"Bunny.net delete error: {e}")
            return False


@app.get("/health")
async def health_check():
    bunny_configured = bool(BUNNY_API_KEY and BUNNY_STORAGE_ZONE)
    return {
        "status": "healthy", 
        "service": "cdn",
        "bunny_configured": bunny_configured,
        "cdn_url": CDN_BASE_URL
    }


@app.post("/api/cdn/upload")
async def upload_file(
    file: UploadFile = File(...),
    folder: str = Form("uploads"),
    access_type: str = Form("public")
):
    """Upload file to CDN"""
    try:
        # Read file content
        content = await file.read()
        
        # Generate path
        file_path = generate_file_path(file.filename, folder)
        
        # Try Bunny.net first, fallback to local
        uploaded_to_bunny = await upload_to_bunny(file_path, content)
        
        if uploaded_to_bunny:
            cdn_url = f"{CDN_BASE_URL}/{file_path}"
            return JSONResponse({
                "success": True,
                "url": cdn_path,
                "path": file_path,
                "size": len(content),
                "type": file.content_type,
                "source": "bunny"
            })
        else:
            # Local storage fallback
            local_path = f"/tmp/{file_path}"
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            async with aiofiles.open(local_path, 'wb') as f:
                await f.write(content)
            
            return JSONResponse({
                "success": True,
                "url": f"/cdn/{file_path}",
                "path": file_path,
                "size": len(content),
                "type": file.content_type,
                "source": "local"
            })
    
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/cdn/files")
async def delete_file(path: str):
    """Delete file from CDN"""
    try:
        # Try Bunny.net first
        deleted_from_bunny = await delete_from_bunny(path)
        
        # Also delete local
        local_path = f"/tmp/{path}"
        if os.path.exists(local_path):
            os.remove(local_path)
        
        return JSONResponse({
            "success": True,
            "path": path,
            "deleted_from_bunny": deleted_from_bunny
        })
    
    except Exception as e:
        logger.error(f"Delete error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cdn/stats")
async def get_cdn_stats():
    """Get CDN usage stats"""
    return JSONResponse({
        "storage_zone": BUNNY_STORAGE_ZONE,
        "cdn_url": CDN_BASE_URL,
        "configured": bool(BUNNY_API_KEY and BUNNY_STORAGE_ZONE)
    })


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8006"))
    uvicorn.run(app, host="0.0.0.0", port=port)
