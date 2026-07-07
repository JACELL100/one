"""Scan history: persist and retrieve a signed-in user's past scans.

Anonymous users still get full functionality from /scan, /size and
/recommend — this router only powers the optional "save & revisit" flow,
scoped to Supabase-authenticated users via ``deps.require_user_id``.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response

from ..deps import require_user_id
from ..schemas import (
    SavedScanResponse,
    SaveScanRequest,
    ScanHistoryItem,
    ScanHistoryResponse,
)
from ..services import db

router = APIRouter(prefix="/scans", tags=["scans"])


def _require_configured() -> None:
    if not db.is_configured():
        raise HTTPException(
            status_code=503,
            detail="Scan history is not configured on this deployment (missing Supabase credentials).",
        )


@router.post("", response_model=SavedScanResponse, status_code=201)
async def save_scan(req: SaveScanRequest, user_id: str = Depends(require_user_id)):
    """Persist a completed scan + performance profile + recommendations."""
    _require_configured()
    try:
        scan_row = await db.insert_row(
            "scans",
            {
                "user_id": user_id,
                "length_mm": req.measurement.length_mm,
                "width_mm": req.measurement.width_mm,
                "confidence": req.measurement.confidence,
                "method": req.measurement.method,
            },
        )
        scan_id = scan_row["id"]

        await db.insert_row(
            "profiles",
            {
                "scan_id": scan_id,
                "user_id": user_id,
                "sport": req.goals.sport,
                "surface": req.goals.surface,
                "cushioning": req.goals.cushioning,
                "use_case": req.goals.use_case,
                "gait_profile": req.gait.gait_profile if req.gait else None,
                "cadence_spm": req.gait.cadence_spm if req.gait else None,
            },
        )

        if req.recommendations:
            await db.insert_row(
                "recommendations",
                {
                    "scan_id": scan_id,
                    "user_id": user_id,
                    "payload": [r.model_dump() for r in req.recommendations],
                },
            )
    except db.DbError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return SavedScanResponse(id=scan_id)


@router.get("", response_model=ScanHistoryResponse)
async def list_scans(user_id: str = Depends(require_user_id)):
    """List this user's saved scans, newest first, with profile + recs embedded."""
    _require_configured()
    try:
        rows = await db.select_rows(
            "scans",
            {
                "user_id": f"eq.{user_id}",
                "order": "created_at.desc",
                "select": "*,profiles(*),recommendations(*)",
                "limit": "50",
            },
        )
    except db.DbError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    items = []
    for row in rows:
        profile = (row.get("profiles") or [None])[0]
        reco_row = (row.get("recommendations") or [None])[0]
        goals = None
        gait = None
        if profile:
            goals = {
                "sport": profile.get("sport") or "running",
                "surface": profile.get("surface") or "road",
                "cushioning": profile.get("cushioning") or "balanced",
                "use_case": profile.get("use_case") or "daily",
            }
            if profile.get("gait_profile"):
                gait = {
                    "gait_profile": profile["gait_profile"],
                    "cadence_spm": profile.get("cadence_spm"),
                    "confidence": 1.0,
                    "descriptor": "",
                }
        items.append(
            ScanHistoryItem(
                id=row["id"],
                created_at=row["created_at"],
                measurement={
                    "length_mm": row["length_mm"],
                    "width_mm": row["width_mm"],
                    "confidence": row["confidence"],
                    "method": row["method"] or "unknown",
                },
                goals=goals,
                gait=gait,
                recommendations=(reco_row or {}).get("payload") or [],
            )
        )
    return ScanHistoryResponse(scans=items)


@router.delete("/{scan_id}", status_code=204)
async def delete_scan(scan_id: str, user_id: str = Depends(require_user_id)):
    """Delete a scan (and its profile/recommendations via FK cascade)."""
    _require_configured()
    try:
        await db.delete_rows(
            "scans", {"id": f"eq.{scan_id}", "user_id": f"eq.{user_id}"}
        )
    except db.DbError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return Response(status_code=204)
