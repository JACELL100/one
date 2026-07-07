"""Recommender ranking tests."""

from app.services import recommender


def test_recommend_returns_ranked_limited_list():
    goals = {"sport": "running", "surface": "road", "cushioning": "plush", "use_case": "daily"}
    out = recommender.recommend(260.0, goals, gait=None, limit=3)
    recs = out["recommendations"]
    assert len(recs) == 3
    # Scores must be non-increasing (ranked).
    scores = [r["match_score"] for r in recs]
    assert scores == sorted(scores, reverse=True)
    assert out["ranker"] == "rules"


def test_plush_road_runner_prefers_glide_cushion():
    goals = {"sport": "running", "surface": "road", "cushioning": "plush", "use_case": "daily"}
    gait = {"gait_profile": "cushion", "cadence_spm": 160, "confidence": 0.8, "descriptor": ""}
    out = recommender.recommend(260.0, goals, gait=gait, limit=6)
    top = out["recommendations"][0]
    assert top["product_id"] == "one8-glide-cushion"
    assert "cushion" in top["rationale"].lower() or "cushioning" in top["rationale"].lower()


def test_stability_trail_runner_prefers_terra_trail():
    goals = {"sport": "running", "surface": "trail", "cushioning": "balanced", "use_case": "daily"}
    gait = {"gait_profile": "stability", "cadence_spm": 175, "confidence": 0.8, "descriptor": ""}
    out = recommender.recommend(265.0, goals, gait=gait, limit=6)
    assert out["recommendations"][0]["product_id"] == "one8-terra-trail"


def test_llm_rewrite_hook_used_and_safe():
    goals = {"sport": "training", "surface": "gym", "cushioning": "firm", "use_case": "daily"}

    def rewrite(text):
        return "AI: " + text

    out = recommender.recommend(258.0, goals, llm_rewrite=rewrite, limit=2)
    assert out["ranker"] == "rules+llm"
    assert out["recommendations"][0]["rationale"].startswith("AI: ")


def test_llm_failure_falls_back_gracefully():
    goals = {"sport": "training", "surface": "gym", "cushioning": "firm", "use_case": "daily"}

    def broken(text):
        raise RuntimeError("api down")

    out = recommender.recommend(258.0, goals, llm_rewrite=broken, limit=2)
    # Still returns templated rationale, not an error.
    assert out["recommendations"][0]["rationale"]
