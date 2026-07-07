"""Deterministic per-model sizing engine.

Given a foot length (mm) and a selected one8 model, pick the size whose
internal last best accommodates the foot plus the model's designed toe
headroom (``fit_offset_mm``). We then classify the fit as snug/true/roomy
based on the residual headroom, and produce a plain-language explanation.
"""

from __future__ import annotations

from typing import Optional

from ..data.catalog import Product, get_product

# Ideal toe headroom over the bare foot for a "true" fit (thumb-width rule).
IDEAL_HEADROOM_MM = 10.0
SNUG_MAX_MM = 6.0    # headroom below this -> snug
ROOMY_MIN_MM = 15.0  # headroom above this -> roomy


def _fit_badge(headroom_mm: float) -> str:
    if headroom_mm < SNUG_MAX_MM:
        return "snug"
    if headroom_mm > ROOMY_MIN_MM:
        return "roomy"
    return "true"


def size_for(product: Product, length_mm: float) -> dict:
    """Return the best size row for the foot in this product."""
    target = length_mm + IDEAL_HEADROOM_MM
    chart = product["size_chart"]

    # Choose the smallest size whose last length >= target; if none, largest.
    chosen = None
    for row in chart:
        if row["length_mm"] >= target:
            chosen = row
            break
    if chosen is None:
        chosen = chart[-1]

    headroom = round(chosen["length_mm"] - length_mm, 1)
    fit = _fit_badge(headroom)
    explanation = (
        f"Your foot measures {length_mm:.0f} mm. The {product['name']} "
        f"{chosen['size_label']} last is {chosen['length_mm']:.0f} mm, leaving "
        f"{headroom:.0f} mm of toe room — a {fit} fit for this model."
    )
    return {
        "product_id": product["id"],
        "size_label": chosen["size_label"],
        "fit": fit,
        "length_mm": length_mm,
        "headroom_mm": headroom,
        "explanation": explanation,
    }


def size_by_product_id(product_id: str, length_mm: float) -> dict:
    return size_for(get_product(product_id), length_mm)
