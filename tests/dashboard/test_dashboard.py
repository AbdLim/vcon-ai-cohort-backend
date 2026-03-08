import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock
from app.core.config import settings

@pytest.mark.asyncio
async def test_dashboard_overview(client: AsyncClient, monkeypatch):
    # Mock the dashboard service get_overview function
    mock_overview = {
        "active_cohorts": 5,
        "latest_sessions": []
    }
    
    mock_get_overview = AsyncMock(return_value=mock_overview)
    monkeypatch.setattr("app.features.dashboard.service.DashboardService.get_overview", mock_get_overview)
    
    response = await client.get(f"{settings.API_V1_STR}/dashboard/overview")
    
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "success"
    
    # Check the wrapped data
    result = response_data["data"]
    assert result["active_cohorts"] == 5
    assert result["latest_sessions"] == []
    
    # Verify the mocked function was called
    mock_get_overview.assert_called_once()
