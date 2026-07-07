"""Thin Supabase REST (PostgREST) client.

We deliberately avoid the heavy ``supabase-py`` SDK (gotrue/postgrest/
storage3/realtime) and instead speak PostgREST directly over ``httpx``,
which is already a dependency. This keeps the backend light and fast to
cold-start on Render's free tier.

All calls use the service-role key server-side (bypasses RLS by design —
Supabase's own recommended pattern for trusted backends), and every query
is manually scoped to ``user_id`` so one user can never read another's rows.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

from ..config import get_settings


def is_configured() -> bool:
    s = get_settings()
    return bool(s.supabase_url and s.supabase_service_key)


def _base_url() -> str:
    s = get_settings()
    return f"{s.supabase_url.rstrip('/')}/rest/v1"


def _headers(prefer: Optional[str] = None) -> Dict[str, str]:
    s = get_settings()
    headers = {
        "apikey": s.supabase_service_key,
        "Authorization": f"Bearer {s.supabase_service_key}",
        "Content-Type": "application/json",
    }
    if prefer:
        headers["Prefer"] = prefer
    return headers


class DbError(Exception):
    """Raised when Supabase/PostgREST returns an error response."""


async def insert_row(table: str, row: Dict[str, Any]) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            f"{_base_url()}/{table}",
            headers=_headers(prefer="return=representation"),
            json=row,
        )
    if resp.status_code >= 400:
        raise DbError(f"insert into {table} failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data[0] if isinstance(data, list) else data


async def select_rows(table: str, params: Dict[str, str]) -> List[Dict[str, Any]]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"{_base_url()}/{table}",
            headers=_headers(),
            params=params,
        )
    if resp.status_code >= 400:
        raise DbError(f"select from {table} failed: {resp.status_code} {resp.text}")
    return resp.json()


async def delete_rows(table: str, params: Dict[str, str]) -> None:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.delete(
            f"{_base_url()}/{table}",
            headers=_headers(prefer="return=minimal"),
            params=params,
        )
    if resp.status_code >= 400:
        raise DbError(f"delete from {table} failed: {resp.status_code} {resp.text}")
