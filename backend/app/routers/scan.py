"""Scan endpoints: foot measurement (image or manual) and gait."""

from fastapi import APIRouter, File, HTTPException, UploadFile

from ..config import get_settings
from ..schemas import (
    FootScanResponse,
    GaitResult,
    ManualMeasurementRequest,
    Measurement,
)
from ..services import cv_pipeline, gait

router = APIRouter(prefix="/scan", tags=["scan"])


@router.post("/foot", response_model=FootScanResponse)
async def scan_foot(image: UploadFile = File(...)):
    """Measure a foot from a photo taken on an A4 sheet."""
    settings = get_settings()
    data = await image.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Empty upload.")
    if len(data) > max_bytes:
        raise HTTPException(status_code=413, detail="File too large.")

    try:
        result = cv_pipeline.analyze_foot_image(data)
    except cv_pipeline.ScanError as exc:
        # Detection failed -> signal manual fallback, do not block the user.
        return FootScanResponse(
            measurement=Measurement(
                length_mm=0.0,
                width_mm=0.0,
                confidence=0.0,
                method="failed",
                notes=f"Scan failed ({exc}). Please enter your foot length.",
            ),
            manual_fallback_recommended=True,
        )

    return FootScanResponse(
        measurement=Measurement(**result),
        manual_fallback_recommended=cv_pipeline.should_fallback(result["confidence"]),
    )


@router.post("/foot/manual", response_model=FootScanResponse)
def scan_foot_manual(req: ManualMeasurementRequest):
    """Manual fallback: build a measurement from entered centimetres."""
    result = cv_pipeline.manual_measurement(req.length_cm, req.width_cm)
    return FootScanResponse(
        measurement=Measurement(**result),
        manual_fallback_recommended=False,
    )


@router.post("/gait", response_model=GaitResult)
def scan_gait(
    cadence_spm: int | None = None,
    vertical_osc_cm: float | None = None,
    pronation_deg: float | None = None,
):
    """Derive a gait support profile from coarse biomechanical signals.

    (Optional step; in production these come from hosted pose estimation.)
    """
    result = gait.derive_gait(cadence_spm, vertical_osc_cm, pronation_deg)
    return GaitResult(**result)
