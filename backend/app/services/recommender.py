"""Hybrid recommendation engine: deterministic scoring + optional LLM rationale.

Scoring is fully deterministic and explainable (demo-safe, reproducible). An
optional hosted-LLM layer can rewrite the rationale in a more natural voice;
when unavailable we use a high-quality templated rationale. The ranker never
depends on the network to produce a result.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from ..data.catalog import CATALOG, Product
from . import sizing

# Feature weights (sum to 1.0). Fit is the dominant factor — this is a fit tool.
W_FIT = 0.40
W_SPORT = 0.20
W_SURFACE = 0.12
W_CUSHION = 0.13
W_GAIT = 0.15

_FIT_SCORE = {"true": 1.0, "snug": 0.72, "roomy": 0.75}


def _score_product(
    product: Product,
    length_mm: float,
    goals: Dict,
    gait: Optional[Dict],
) -> Dict:
    size = sizing.size_for(product, length_mm)
    fit_score = _FIT_SCORE[size["fit"]]

    sport_score = 1.0 if product["sport"] == goals.get("sport") else 0.35
    surface_score = (
        1.0
        if product["surface"] == goals.get("surface")
        else (0.7 if product["surface"] == "mixed" or goals.get("surface") == "mixed" else 0.4)
    )
    cushion_score = 1.0 if product["cushioning"] == goals.get("cushioning") else 0.5

    if gait and gait.get("gait_profile"):
        gait_score = 1.0 if product["support"] == gait["gait_profile"] else 0.5
    else:
        gait_score = 0.6  # neutral prior when no gait signal

    total = (
        W_FIT * fit_score
        + W_SPORT * sport_score
        + W_SURFACE * surface_score
        + W_CUSHION * cushion_score
        + W_GAIT * gait_score
    )
    return {"size": size, "score": round(total, 4)}


def _rationale(product: Product, size: Dict, goals: Dict, gait: Optional[Dict]) -> str:
    parts = [
        f"Sized {size['size_label']} for a {size['fit']} fit "
        f"({size['headroom_mm']:.0f} mm toe room)."
    ]
    if product["sport"] == goals.get("sport"):
        parts.append(f"Built for {goals['sport']}.")
    if product["surface"] == goals.get("surface"):
        parts.append(f"Tuned for {goals['surface']} surfaces.")
    if product["cushioning"] == goals.get("cushioning"):
        parts.append(f"{product['cushioning'].capitalize()} cushioning as you prefer.")
    if gait and product["support"] == gait.get("gait_profile"):
        parts.append(f"Supports your {gait['gait_profile']} gait.")
    return " ".join(parts)


def recommend(
    length_mm: float,
    goals: Dict,
    gait: Optional[Dict] = None,
    limit: int = 3,
    llm_rewrite=None,
) -> Dict:
    """Return ranked recommendations. ``llm_rewrite`` is an optional callable
    ``(text) -> text`` for the hosted-LLM rationale layer."""
    scored: List[Dict] = []
    for product in CATALOG:
        result = _score_product(product, length_mm, goals, gait)
        rationale = _rationale(product, result["size"], goals, gait)
        if llm_rewrite is not None:
            try:
                rationale = llm_rewrite(rationale)
            except Exception:
                pass  # fall back to templated rationale
        scored.append(
            {
                "product_id": product["id"],
                "name": product["name"],
                "price_inr": product["price_inr"],
                "image_url": product["image_url"],
                "size_label": result["size"]["size_label"],
                "fit": result["size"]["fit"],
                "match_score": result["score"],
                "rationale": rationale,
            }
        )

    scored.sort(key=lambda r: r["match_score"], reverse=True)
    ranker = "rules+llm" if llm_rewrite is not None else "rules"
    return {"recommendations": scored[:limit], "ranker": ranker}
