import pytest
import json
from app.services.vcon_service import VconBuilder

def test_vcon_builder_initialization():
    builder = VconBuilder(session_id=101, cohort_id=5)
    
    # Serialize to dict to check keys
    vcon_json = builder.serialize()
    vcon_dict = json.loads(vcon_json)
    
    assert "uuid" in vcon_dict
    assert "vcon" in vcon_dict
    assert vcon_dict["vcon"] == "0.0.1"
    
    # Check initialized metadata attachment
    attachments = vcon_dict.get("attachments", [])
    assert len(attachments) == 1
    assert attachments[0]["body"]["session_id"] == 101
    assert attachments[0]["body"]["cohort_id"] == 5

def test_vcon_builder_add_recording():
    builder = VconBuilder(session_id=101, cohort_id=5)
    url = "https://example.com/mock-video.mp4"
    builder.add_recording(file_path="mock-video.mp4", url=url)
    
    vcon_dict = json.loads(builder.serialize())
    dialogs = vcon_dict.get("dialog", [])
    assert len(dialogs) == 1
    assert dialogs[0]["url"] == url
    assert dialogs[0]["mimetype"] == "video/mp4"

def test_vcon_builder_add_analysis():
    builder = VconBuilder(session_id=101, cohort_id=5)
    
    # Setup prerequisite dialog for analysis
    builder.add_recording(file_path="video.mp4", url="https://x")
    
    mock_analysis = {"text": "Hello world, welcome to cohort"}
    builder.add_analysis(analysis_type="transcript", result=mock_analysis, vendor="mock-ai")
    
    vcon_dict = json.loads(builder.serialize())
    analyses = vcon_dict.get("analysis", [])
    assert len(analyses) == 1
    assert analyses[0]["vendor"] == "mock-ai"
    assert "Hello world" in analyses[0]["body"]["text"]
