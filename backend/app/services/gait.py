"""Gait/cadence descriptor derivation.

In production this consumes pose keypoints from a hosted pose-estimation
model (e.g. NVIDIA/HF) over sampled video frames. For the free-tier demo we
expose a deterministic descriptor derived from a compact set of numeric
signals (cadence + vertical oscillation + pronation hint), so the endpoint is
fully functional and testable without a GPU.
"""

from __future__ import annotations

from typing import Optional


def derive_gait(
    cadence_spm: Optional[int] = None,
    vertical_osc_cm: Optional[float] = None,
    pronation_deg: Optional[float] = None,
) -> dict:
    """Map coarse biomechanical signals to a support profile.

    - High pronation -> stability
    - High vertical oscillation / low cadence -> cushion
    - Otherwise -> neutral
    """
    signals = 0
    confidence = 0.5

    profile = "neutral"
    if pronation_deg is not None and pronation_deg >= 8.0:
        profile = "stability"
        signals += 1
    elif (vertical_osc_cm is not None and vertical_osc_cm >= 9.0) or (
        cadence_spm is not None and cadence_spm < 165
    ):
        profile = "cushion"
        signals += 1

    if cadence_spm is not None:
        confidence += 0.2
    if vertical_osc_cm is not None:
        confidence += 0.15
    if pronation_deg is not None:
        confidence += 0.15
    confidence = min(1.0, confidence)

    descriptor = {
        "neutral": "Balanced, efficient stride — a neutral platform suits you.",
        "cushion": "Longer ground contact / softer landing — extra cushioning helps.",
        "stability": "Some inward roll detected — a stability shoe supports your gait.",
    }[profile]

    return {
        "gait_profile": profile,
        "cadence_spm": cadence_spm,
        "confidence": round(confidence, 3),
        "descriptor": descriptor,
    }
