import httpx
from typing import List, Dict, Optional
from fastapi import HTTPException

BLOG_SERVICE_URL = "http://blog:8003"
INTERNAL_API_KEY = "nekwasar-internal-admin-key"  # Should be env var in production


class BlogServiceClient:
    @staticmethod
    async def _request(method: str, path: str, **kwargs) -> Dict:
        headers = {
            "X-Internal-Api-Key": INTERNAL_API_KEY,
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method,
                    f"{BLOG_SERVICE_URL}{path}",
                    headers=headers,
                    timeout=10.0,
                    **kwargs,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise HTTPException(
                    status_code=503, detail=f"Blog service unavailable: {str(e)}"
                )

    @staticmethod
    async def get_posts() -> Dict:
        return await BlogServiceClient._request("GET", "/api/admin/posts")

    @staticmethod
    async def get_post(post_id: int) -> Dict:
        return await BlogServiceClient._request("GET", f"/api/admin/posts/{post_id}")

    @staticmethod
    async def create_post(post_data: Dict) -> Dict:
        return await BlogServiceClient._request(
            "POST", "/api/admin/posts", json=post_data
        )

    @staticmethod
    async def update_post(post_id: int, post_data: Dict) -> Dict:
        return await BlogServiceClient._request(
            "PUT", f"/api/admin/posts/{post_id}", json=post_data
        )

    @staticmethod
    async def delete_post(post_id: int) -> Dict:
        return await BlogServiceClient._request("DELETE", f"/api/admin/posts/{post_id}")

    @staticmethod
    async def get_tags() -> Dict:
        return await BlogServiceClient._request("GET", "/api/admin/tags")

    @staticmethod
    async def create_tag(tag_data: Dict) -> Dict:
        return await BlogServiceClient._request(
            "POST", "/api/admin/tags", json=tag_data
        )

    @staticmethod
    async def delete_tag(tag_id: int) -> Dict:
        return await BlogServiceClient._request("DELETE", f"/api/admin/tags/{tag_id}")

    @staticmethod
    async def get_categories() -> Dict:
        return await BlogServiceClient._request("GET", "/api/admin/categories")

    @staticmethod
    async def get_comments(post_id: Optional[int] = None) -> Dict:
        path = "/api/admin/comments"
        if post_id:
            path += f"?post_id={post_id}"
        return await BlogServiceClient._request("GET", path)

    @staticmethod
    async def moderate_comment(comment_id: int, approved: bool) -> Dict:
        return await BlogServiceClient._request(
            "PUT",
            f"/api/admin/comments/{comment_id}/moderate",
            json={"approved": approved},
        )

    @staticmethod
    async def get_stats() -> Dict:
        return await BlogServiceClient._request("GET", "/api/admin/stats")
