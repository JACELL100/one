"""Pure-Python geometry for reference-object scaling.

The core idea behind one8 FitLab: a foot photographed on a standard A4 sheet
can be measured in real-world units because A4 has known dimensions
(210 x 297 mm). We detect the sheet, compute a pixels-per-mm scale, then apply
that scale to the foot's pixel bounding geometry.

This module is intentionally dependency-free (no OpenCV/numpy) so the math is
unit-testable in isolation and runs on any free tier. The OpenCV-backed
detection lives in ``cv_pipeline.py`` and delegates the arithmetic here.
"""

from __future__ import annotations

from dataclasses import dataclass

# ISO 216 A4 dimensions in millimetres.
A4_LONG_MM = 297.0
A4_SHORT_MM = 210.0


@dataclass(frozen=True)
class ScaleResult:
    mm_per_px: float
    confidence: float


def compute_scale(
    ref_long_px: float,
    ref_short_px: float,
    *,
    expected_long_mm: float = A4_LONG_MM,
    expected_short_mm: float = A4_SHORT_MM,
) -> ScaleResult:
    """Compute millimetres-per-pixel from a detected reference rectangle.

    We average the scale derived from both edges and derive a confidence
    from how closely the detected aspect ratio matches the true A4 ratio —
    a strong signal that we actually found the sheet (and not noise).
    """
    if ref_long_px <= 0 or ref_short_px <= 0:
        raise ValueError("reference edge lengths must be positive")

    # Orient: longest measured edge maps to the long side of the sheet.
    long_px = max(ref_long_px, ref_short_px)
    short_px = min(ref_long_px, ref_short_px)

    scale_long = expected_long_mm / long_px
    scale_short = expected_short_mm / short_px
    mm_per_px = (scale_long + scale_short) / 2.0

    expected_ratio = expected_long_mm / expected_short_mm
    detected_ratio = long_px / short_px
    ratio_error = abs(detected_ratio - expected_ratio) / expected_ratio
    # Map 0% error -> 1.0 confidence, 25%+ error -> ~0.0.
    confidence = max(0.0, min(1.0, 1.0 - ratio_error / 0.25))

    return ScaleResult(mm_per_px=mm_per_px, confidence=confidence)


@dataclass(frozen=True)
class FootMeasurement:
    length_mm: float
    width_mm: float
    confidence: float


def measure_foot(
    foot_length_px: float,
    foot_width_px: float,
    scale: ScaleResult,
    *,
    mask_quality: float = 1.0,
) -> FootMeasurement:
    """Convert foot pixel dimensions to millimetres using the sheet scale.

    ``mask_quality`` (0..1) reflects how clean the foot segmentation was.
    Final confidence blends scale confidence and mask quality, then is
    penalised if the resulting measurement is physiologically implausible.
    """
    if foot_length_px <= 0 or foot_width_px <= 0:
        raise ValueError("foot pixel dimensions must be positive")

    length_mm = foot_length_px * scale.mm_per_px
    width_mm = foot_width_px * scale.mm_per_px

    confidence = scale.confidence * max(0.0, min(1.0, mask_quality))

    # Plausibility gate: adult feet ~ 200-320mm long, width/length ~0.30-0.45.
    if not (180.0 <= length_mm <= 340.0):
        confidence *= 0.4
    ratio = width_mm / length_mm if length_mm else 0
    if not (0.28 <= ratio <= 0.48):
        confidence *= 0.6

    return FootMeasurement(
        length_mm=round(length_mm, 1),
        width_mm=round(width_mm, 1),
        confidence=round(max(0.0, min(1.0, confidence)), 3),
    )


# Below this confidence we recommend the manual cm fallback so the user is
# never blocked by a bad photo.
MANUAL_FALLBACK_THRESHOLD = 0.55
