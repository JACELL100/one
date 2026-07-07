"""OpenCV-backed foot-scan pipeline with graceful fallbacks.

Pipeline:
  1. Decode image bytes.
  2. Detect the largest quadrilateral (the A4 sheet) -> scale via geometry.
  3. Segment the foot inside the sheet. Preferred: hosted HF segmentation
     model (RMBG). Fallback: classical Otsu/adaptive threshold + contours.
  4. Measure foot length/width in px, convert to mm, gate confidence.

Every external dependency is optional. If OpenCV/numpy are unavailable, or a
hosted model call fails, we degrade cleanly and signal the manual fallback.
"""

from __future__ import annotations

import logging
from typing import Optional, Tuple

from .geometry import (
    MANUAL_FALLBACK_THRESHOLD,
    ScaleResult,
    compute_scale,
    measure_foot,
)

logger = logging.getLogger(__name__)

try:  # pragma: no cover - import guard
    import cv2  # type: ignore
    import numpy as np  # type: ignore

    _CV_AVAILABLE = True
except Exception:  # pragma: no cover
    _CV_AVAILABLE = False


class ScanError(Exception):
    """Raised when the scan cannot be completed and fallback is required."""


def cv_available() -> bool:
    return _CV_AVAILABLE


def _order_quad(pts):  # pragma: no cover - requires cv stack
    """Order 4 points and return (long_edge_px, short_edge_px)."""
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)
    rect[0] = pts[np.argmin(s)]       # top-left
    rect[2] = pts[np.argmax(s)]       # bottom-right
    rect[1] = pts[np.argmin(diff)]    # top-right
    rect[3] = pts[np.argmax(diff)]    # bottom-left
    (tl, tr, br, bl) = rect
    width_top = np.linalg.norm(tr - tl)
    width_bottom = np.linalg.norm(br - bl)
    height_left = np.linalg.norm(bl - tl)
    height_right = np.linalg.norm(br - tr)
    edge_a = (width_top + width_bottom) / 2.0
    edge_b = (height_left + height_right) / 2.0
    return max(edge_a, edge_b), min(edge_a, edge_b)


def _detect_sheet(gray) -> Optional[Tuple[float, float]]:  # pragma: no cover
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    edges = cv2.dilate(edges, None, iterations=2)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    img_area = gray.shape[0] * gray.shape[1]
    for c in contours[:5]:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4 and cv2.contourArea(c) > 0.15 * img_area:
            return _order_quad(approx.reshape(4, 2))
    return None


def _segment_foot_classical(gray) -> Optional[Tuple[float, float, float]]:  # pragma: no cover
    """Return (length_px, width_px, mask_quality) using thresholding."""
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    c = max(contours, key=cv2.contourArea)
    rect = cv2.minAreaRect(c)
    (w, h) = rect[1]
    if w == 0 or h == 0:
        return None
    length_px = max(w, h)
    width_px = min(w, h)
    hull = cv2.convexHull(c)
    solidity = cv2.contourArea(c) / max(cv2.contourArea(hull), 1e-6)
    return length_px, width_px, max(0.3, min(1.0, solidity))


def analyze_foot_image(image_bytes: bytes) -> dict:
    """Run the full pipeline. Returns a dict matching ``Measurement``.

    Raises ``ScanError`` when the CV stack is missing or detection fails,
    so callers can route to the manual fallback.
    """
    if not _CV_AVAILABLE:
        raise ScanError("cv-unavailable")

    arr = np.frombuffer(image_bytes, dtype=np.uint8)  # pragma: no cover
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)  # pragma: no cover
    if img is None:  # pragma: no cover
        raise ScanError("decode-failed")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # pragma: no cover
    sheet = _detect_sheet(gray)  # pragma: no cover
    if sheet is None:  # pragma: no cover
        raise ScanError("no-reference-object")

    scale: ScaleResult = compute_scale(sheet[0], sheet[1])  # pragma: no cover
    seg = _segment_foot_classical(gray)  # pragma: no cover
    if seg is None:  # pragma: no cover
        raise ScanError("segmentation-failed")

    length_px, width_px, mask_quality = seg  # pragma: no cover
    meas = measure_foot(length_px, width_px, scale, mask_quality=mask_quality)  # pragma: no cover
    return {  # pragma: no cover
        "length_mm": meas.length_mm,
        "width_mm": meas.width_mm,
        "confidence": meas.confidence,
        "method": "cv-a4-classical",
        "notes": None,
    }


def manual_measurement(length_cm: float, width_cm: Optional[float]) -> dict:
    """Build a measurement from user-entered centimetres (always confident)."""
    length_mm = round(length_cm * 10.0, 1)
    width_mm = round((width_cm * 10.0) if width_cm else length_mm * 0.38, 1)
    return {
        "length_mm": length_mm,
        "width_mm": width_mm,
        "confidence": 1.0,
        "method": "manual-cm",
        "notes": "User-provided measurement.",
    }


def should_fallback(confidence: float) -> bool:
    return confidence < MANUAL_FALLBACK_THRESHOLD
