"""Auth dependency: verifies Supabase-issued JWTs without any extra SDK.

Supabase signs user access tokens with the project's JWT secret (HS256).
We decode and verify that signature directly with PyJWT. If no secret is
configured (local/demo without Supabase), auth degrades to "anonymous"
rather than hard-failing the whole API.
"""

from __future__ import annotations

from typing import Optional

import jwt
from fastapi import Header, HTTPException, status

from .config import get_settings


def _decode(token: str) -> Optional[dict]:
    settings = get_settings()
    if not settings.supabase_jwt_secret:
        return None
    try:
        return jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except jwt.PyJWTError:
        return None


def get_optional_user_id(
    authorization: Optional[str] = Header(default=None),
) -> Optional[str]:
    """Return the Supabase ``auth.uid()`` if a valid bearer token is present, else None."""
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    token = authorization.split(" ", 1)[1].strip()
    payload = _decode(token)
    return payload.get("sub") if payload else None


def require_user_id(authorization: Optional[str] = Header(default=None)) -> str:
    """Same as above, but raises 401 when there is no valid authenticated user."""
    user_id = get_optional_user_id(authorization)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sign in required to use scan history.",
        )
    return user_id
