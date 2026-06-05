"""
API client wrapper for communicating with the FastAPI backend.

Uses the stdlib urllib.request module so no extra HTTP
library dependency is needed for the Tkinter frontend.
"""

import json
import urllib.request
import urllib.error
from typing import Optional, Any
from frontend.config import API_BASE_URL


class ApiClient:
    """
    Thin HTTP client that wraps common REST verbs.

    Automatically prefixes every path with API_BASE_URL
    and attaches the JWT token when available.
    """

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.token: Optional[str] = None

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _request(
        self, method: str, path: str, data: Optional[dict] = None
    ) -> tuple[int, Any]:
        url = f"{self.base_url}{path}"
        body = json.dumps(data).encode("utf-8") if data else None
        req = urllib.request.Request(
            url, data=body, headers=self._headers(), method=method
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode("utf-8")
                return resp.status, json.loads(content) if content else None
        except urllib.error.HTTPError as e:
            content = e.read().decode("utf-8", errors="replace")
            try:
                return e.code, json.loads(content) if content else {"detail": str(e)}
            except json.JSONDecodeError:
                return e.code, {"detail": content or str(e)}

    def get(self, path: str) -> tuple[int, Any]:
        return self._request("GET", path)

    def post(self, path: str, data: dict) -> tuple[int, Any]:
        return self._request("POST", path, data)

    def put(self, path: str, data: dict) -> tuple[int, Any]:
        return self._request("PUT", path, data)

    def delete(self, path: str) -> tuple[int, Any]:
        return self._request("DELETE", path)


# Singleton instance shared across all frontend views
api_client = ApiClient()
