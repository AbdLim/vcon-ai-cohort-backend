import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock
from app.core.config import settings

@pytest.mark.asyncio
async def test_get_cohort_with_sessions(client: AsyncClient, monkeypatch):
    # Mock the cohort service get_cohort function
    class MockCohort:
        id = 1
        name = "Test Cohort"
        description = "A mock cohort"
        organization_id = 99
        created_at = "2026-03-08T12:00:00Z"
        updated_at = "2026-03-08T12:00:00Z"
        sessions = [] # Empty list of sessions

    mock_cohort = MockCohort()
    
    mock_get_cohort = AsyncMock(return_value=mock_cohort)
    monkeypatch.setattr("app.features.cohorts.service.CohortService.get_cohort", mock_get_cohort)
    
    response = await client.get(f"{settings.API_V1_STR}/cohorts/1")
    
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "success"
    
    # Check the wrapped data
    result = response_data["data"]
    assert result["id"] == 1
    assert result["name"] == "Test Cohort"
    assert "sessions" in result
    assert result["sessions"] == []
    
    # Verify the mocked function was called
    mock_get_cohort.assert_called_once_with(1)
