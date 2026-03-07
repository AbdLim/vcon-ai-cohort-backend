import pytest
from httpx import AsyncClient
from app.core.config import settings
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
async def test_upload_session(client: AsyncClient):
    # Setup test file
    file_content = b"fake video content"
    files = {"file": ("test_video.mp4", file_content, "video/mp4")}
    data = {
        "title": "Test Cohort Session",
        "cohort_id": 1
    }
    
    # Mock the celery delay call so it doesn't actually try to connect to Redis
    with patch("app.features.sessions.service.process_session_task.delay") as mock_delay:
        mock_task = MagicMock()
        mock_task.id = "mock-task-id-1234"
        mock_delay.return_value = mock_task
        
        response = await client.post(
            f"{settings.API_V1_STR}/sessions/upload",
            data=data,
            files=files
        )
        
        assert response.status_code == 202
        response_data = response.json()
        assert response_data["status"] == "success"
        
        # Check the wrapped data
        result = response_data["data"]
        assert result["task_id"] == "mock-task-id-1234"
        assert result["status"] == "processing"
        
        # Verify the celery task was called with correct structure
        mock_delay.assert_called_once()
        kwargs = mock_delay.call_args.kwargs
        assert "session_id" in kwargs
        assert kwargs["filename"] == "test_video.mp4"
        assert "filepath" in kwargs

@pytest.mark.asyncio
async def test_import_session_url(client: AsyncClient):
    data = {
        "title": "Test URL Cohort Session",
        "cohort_id": 1,
        "url": "https://example.com/video.mp4"
    }
    
    with patch("app.features.sessions.service.process_session_task.delay") as mock_delay:
        mock_task = MagicMock()
        mock_task.id = "mock-task-id-5678"
        mock_delay.return_value = mock_task
        
        response = await client.post(
            f"{settings.API_V1_STR}/sessions/url",
            json=data,
        )
        
        assert response.status_code == 202
        response_data = response.json()
        assert response_data["status"] == "success"
        
        result = response_data["data"]
        assert result["task_id"] == "mock-task-id-5678"
        assert result["status"] == "processing"
        
        mock_delay.assert_called_once()
        kwargs = mock_delay.call_args.kwargs
        assert "session_id" in kwargs
        assert kwargs["file_url"] == "https://example.com/video.mp4"
        assert kwargs["filename"] is None
        assert kwargs["filepath"] is None
