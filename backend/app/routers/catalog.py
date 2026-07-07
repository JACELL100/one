"""Catalog endpoint — serves the curated one8 demo models."""

from fastapi import APIRouter

from ..data.catalog import CATALOG

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("")
def list_catalog():
    """Return all one8 models (chart trimmed to keep payload small)."""
    return {
        "products": [
            {
                "id": p["id"],
                "name": p["name"],
                "tagline": p["tagline"],
                "price_inr": p["price_inr"],
                "image_url": p["image_url"],
                "sport": p["sport"],
                "surface": p["surface"],
                "cushioning": p["cushioning"],
                "support": p["support"],
                "width_class": p["width_class"],
            }
            for p in CATALOG
        ]
    }
