import pytest

from app.schemas.analysis import AnalysisResponse

ANALYSIS_URL = "/analysis"


@pytest.mark.asyncio
async def test_analysis_no_cache(async_client):
    response = await async_client.get(f"{ANALYSIS_URL}/AAPL")
    assert response.status_code in (401, 503)


@pytest.mark.asyncio
async def test_analysis_requires_auth(async_client):
    response = await async_client.get(f"{ANALYSIS_URL}/AAPL")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_analysis_schema():
    from datetime import datetime, timezone
    resp = AnalysisResponse(
        ticker="AAPL",
        company_name="Apple Inc.",
        sector="Technology",
        price=None,
        cached_at=datetime.now(timezone.utc),
    )
    data = resp.model_dump()
    assert data["ticker"] == "AAPL"
    assert data["sector"] == "Technology"
    assert data["fundamentals"] is None
    assert data["health_score"] is None
