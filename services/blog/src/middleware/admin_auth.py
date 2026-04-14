from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

INTERNAL_API_KEY = "nekwasar-internal-admin-key"  # Should be env var in production


class AdminAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Only protect /api/admin/* routes
        if request.url.path.startswith("/api/admin/"):
            api_key = request.headers.get("X-Internal-Api-Key")

            if not api_key or api_key != INTERNAL_API_KEY:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or missing internal API key",
                )

        response = await call_next(request)
        return response
