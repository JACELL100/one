"""Pydantic request/response contracts shared across the API."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

FitBadge = Literal["snug", "true", "roomy"]
GaitProfile = Literal["neutral", "cushion", "stability"]


class Measurement(BaseModel):
    length_mm: float = Field(..., description="Foot length in millimetres.")
    width_mm: float = Field(..., description="Foot width in millimetres.")
    confidence: float = Field(..., ge=0.0, le=1.0)
    method: str = Field(..., description="How the measurement was derived.")
    notes: Optional[str] = None


class FootScanResponse(BaseModel):
    measurement: Measurement
    manual_fallback_recommended: bool


class ManualMeasurementRequest(BaseModel):
    length_cm: float = Field(..., gt=10, lt=40)
    width_cm: Optional[float] = Field(default=None, gt=4, lt=20)


class SizeRequest(BaseModel):
    length_mm: float = Field(..., gt=100, lt=400)
    width_mm: Optional[float] = Field(default=None, gt=40, lt=200)
    product_id: str


class SizeResult(BaseModel):
    product_id: str
    size_label: str
    fit: FitBadge
    length_mm: float
    headroom_mm: float
    explanation: str


class GoalsProfile(BaseModel):
    sport: Literal["running", "training", "lifestyle", "court"] = "running"
    surface: Literal["road", "trail", "track", "gym", "mixed"] = "road"
    cushioning: Literal["firm", "balanced", "plush"] = "balanced"
    use_case: Literal["daily", "race", "recovery", "allday"] = "daily"


class GaitResult(BaseModel):
    gait_profile: GaitProfile
    cadence_spm: Optional[int] = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    descriptor: str


class RecommendRequest(BaseModel):
    length_mm: float = Field(..., gt=100, lt=400)
    width_mm: Optional[float] = Field(default=None, gt=40, lt=200)
    goals: GoalsProfile = GoalsProfile()
    gait: Optional[GaitResult] = None
    limit: int = Field(default=3, ge=1, le=10)


class Recommendation(BaseModel):
    product_id: str
    name: str
    price_inr: int
    image_url: str
    size_label: str
    fit: FitBadge
    match_score: float = Field(..., ge=0.0, le=1.0)
    rationale: str


class RecommendResponse(BaseModel):
    recommendations: List[Recommendation]
    ranker: str = Field(..., description="Which ranking path produced the result.")


class SaveScanRequest(BaseModel):
    """Payload persisted when a signed-in user saves a completed scan."""

    measurement: Measurement
    goals: GoalsProfile
    gait: Optional[GaitResult] = None
    recommendations: List[Recommendation] = Field(default_factory=list)


class ScanHistoryItem(BaseModel):
    id: str
    created_at: str
    measurement: Measurement
    goals: Optional[GoalsProfile] = None
    gait: Optional[GaitResult] = None
    recommendations: List[Recommendation] = Field(default_factory=list)


class ScanHistoryResponse(BaseModel):
    scans: List[ScanHistoryItem]


class SavedScanResponse(BaseModel):
    id: str
