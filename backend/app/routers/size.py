"""Sizing endpoint: measurement + model -> size + fit badge."""

from fastapi import APIRouter, HTTPException

from ..schemas import SizeRequest, SizeResult
from ..services import sizing

router = APIRouter(prefix="/size", tags=["size"])


@router.post("", response_model=SizeResult)
def compute_size(req: SizeRequest):
    try:
        result = sizing.size_by_product_id(req.product_id, req.length_mm)
    except KeyError:
        raise HTTPException(status_code=404, detail="Unknown product_id.")
    return SizeResult(**result)
