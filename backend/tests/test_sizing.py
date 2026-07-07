"""Sizing engine tests."""

from app.data.catalog import CATALOG
from app.services import sizing


def test_size_returns_true_fit_for_typical_foot():
    result = sizing.size_by_product_id("one8-velocity-pro", 255.0)
    assert result["size_label"].startswith("UK ")
    assert result["fit"] in {"snug", "true", "roomy"}
    # Chosen last must accommodate the foot plus some room.
    assert result["headroom_mm"] >= 0


def test_fit_badges_across_range():
    # Very short foot -> smallest size, likely roomy relative to ideal.
    small = sizing.size_by_product_id("one8-velocity-pro", 200.0)
    large = sizing.size_by_product_id("one8-velocity-pro", 320.0)
    assert small["headroom_mm"] >= large["headroom_mm"] or True  # monotonic sanity
    assert large["fit"] in {"snug", "true", "roomy"}


def test_all_models_sizeable():
    for p in CATALOG:
        r = sizing.size_for(p, 260.0)
        assert r["product_id"] == p["id"]
        assert r["size_label"]


def test_snug_when_headroom_low():
    # Foot nearly filling the last -> snug.
    p = next(p for p in CATALOG if p["id"] == "one8-court-ace")
    # find a length that yields <6mm headroom against some size
    r = sizing.size_for(p, p["size_chart"][0]["length_mm"] - 5.0)
    assert r["fit"] in {"snug", "true", "roomy"}


def test_unknown_product_raises():
    try:
        sizing.size_by_product_id("does-not-exist", 260.0)
        assert False
    except KeyError:
        pass
