"""Unit tests for the reference-object scaling math (no CV deps needed)."""

import math

from app.services.geometry import (
    A4_LONG_MM,
    A4_SHORT_MM,
    compute_scale,
    measure_foot,
)


def test_scale_perfect_a4_ratio_high_confidence():
    # A perfectly detected A4 at 1000x707 px (297:210 ratio).
    scale = compute_scale(1000.0, 707.0)
    assert scale.confidence > 0.95
    # 297mm over 1000px => ~0.297 mm/px; averaged with short edge.
    assert math.isclose(scale.mm_per_px, (297 / 1000 + 210 / 707) / 2, rel_tol=1e-6)


def test_scale_bad_ratio_low_confidence():
    # A square (ratio 1.0) is nothing like A4 -> low confidence.
    scale = compute_scale(500.0, 500.0)
    assert scale.confidence < 0.2


def test_measure_foot_realistic():
    # 1000px long edge of A4 => 0.297 mm/px on the long edge.
    scale = compute_scale(1000.0, 707.0)
    # A ~260mm foot should be ~875px long at this scale.
    foot_len_px = 260.0 / scale.mm_per_px
    foot_wid_px = 98.0 / scale.mm_per_px
    m = measure_foot(foot_len_px, foot_wid_px, scale)
    assert abs(m.length_mm - 260.0) < 3.0
    assert abs(m.width_mm - 98.0) < 3.0
    assert m.confidence > 0.9


def test_measure_foot_implausible_penalised():
    scale = compute_scale(1000.0, 707.0)
    # Absurdly long "foot" (500mm) should be confidence-penalised.
    foot_len_px = 500.0 / scale.mm_per_px
    foot_wid_px = 150.0 / scale.mm_per_px
    m = measure_foot(foot_len_px, foot_wid_px, scale)
    assert m.confidence < 0.5


def test_scale_rejects_nonpositive():
    for args in [(0, 100), (100, 0), (-5, 10)]:
        try:
            compute_scale(*args)
            assert False, "expected ValueError"
        except ValueError:
            pass
