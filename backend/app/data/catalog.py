"""Curated mock one8 catalog with per-model size charts and attributes.

This is the single source of truth for the demo. It is also exported to
SQL seed data in ``/supabase``. Each model fits slightly differently, which
is the whole point of per-model sizing rather than a global chart.
"""

from typing import Dict, List, TypedDict


class SizeRow(TypedDict):
    size_label: str
    length_mm: float  # internal last length at this size (foot length upper bound)


class Product(TypedDict):
    id: str
    name: str
    tagline: str
    price_inr: int
    image_url: str
    sport: str          # running | training | lifestyle | court
    surface: str        # road | trail | track | gym | mixed
    cushioning: str     # firm | balanced | plush
    support: str        # neutral | cushion | stability  (maps to gait_profile)
    width_class: str    # narrow | standard | wide
    # per-model last: extra room designed into the shoe (mm) at true fit.
    fit_offset_mm: float
    size_chart: List[SizeRow]


def _chart(base_uk: int, start_mm: float) -> List[SizeRow]:
    """Generate a UK size chart in ~8.5mm steps (half-size ~= 4.2mm)."""
    rows: List[SizeRow] = []
    mm = start_mm
    for i in range(0, 9):
        label = f"UK {base_uk + i}"
        rows.append({"size_label": label, "length_mm": round(mm, 1)})
        mm += 8.5
    return rows


CATALOG: List[Product] = [
    {
        "id": "one8-velocity-pro",
        "name": "one8 Velocity Pro",
        "tagline": "Race-day carbon-plated road racer.",
        "price_inr": 12999,
        "image_url": "/products/velocity-pro.svg",
        "sport": "running",
        "surface": "road",
        "cushioning": "firm",
        "support": "neutral",
        "width_class": "standard",
        "fit_offset_mm": 8.0,
        "size_chart": _chart(5, 247.0),
    },
    {
        "id": "one8-glide-cushion",
        "name": "one8 Glide Cushion",
        "tagline": "Max-cushion daily trainer for easy miles.",
        "price_inr": 9999,
        "image_url": "/products/glide-cushion.svg",
        "sport": "running",
        "surface": "road",
        "cushioning": "plush",
        "support": "cushion",
        "width_class": "wide",
        "fit_offset_mm": 12.0,
        "size_chart": _chart(5, 250.0),
    },
    {
        "id": "one8-terra-trail",
        "name": "one8 Terra Trail",
        "tagline": "Grippy, protective off-road companion.",
        "price_inr": 11499,
        "image_url": "/products/terra-trail.svg",
        "sport": "running",
        "surface": "trail",
        "cushioning": "balanced",
        "support": "stability",
        "width_class": "wide",
        "fit_offset_mm": 11.0,
        "size_chart": _chart(5, 249.0),
    },
    {
        "id": "one8-forge-train",
        "name": "one8 Forge Trainer",
        "tagline": "Stable, flat platform for the gym floor.",
        "price_inr": 8499,
        "image_url": "/products/forge-train.svg",
        "sport": "training",
        "surface": "gym",
        "cushioning": "firm",
        "support": "stability",
        "width_class": "standard",
        "fit_offset_mm": 9.0,
        "size_chart": _chart(5, 246.0),
    },
    {
        "id": "one8-court-ace",
        "name": "one8 Court Ace",
        "tagline": "Quick, locked-in multi-court shoe.",
        "price_inr": 8999,
        "image_url": "/products/court-ace.svg",
        "sport": "court",
        "surface": "mixed",
        "cushioning": "balanced",
        "support": "neutral",
        "width_class": "narrow",
        "fit_offset_mm": 7.0,
        "size_chart": _chart(5, 245.0),
    },
    {
        "id": "one8-street-edit",
        "name": "one8 Street Edit",
        "tagline": "All-day lifestyle sneaker, athletic DNA.",
        "price_inr": 6999,
        "image_url": "/products/street-edit.svg",
        "sport": "lifestyle",
        "surface": "road",
        "cushioning": "plush",
        "support": "neutral",
        "width_class": "standard",
        "fit_offset_mm": 10.0,
        "size_chart": _chart(5, 248.0),
    },
]

CATALOG_BY_ID: Dict[str, Product] = {p["id"]: p for p in CATALOG}


def get_product(product_id: str) -> Product:
    if product_id not in CATALOG_BY_ID:
        raise KeyError(product_id)
    return CATALOG_BY_ID[product_id]
