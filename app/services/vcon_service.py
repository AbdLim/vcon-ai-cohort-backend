import json
import uuid
import logging
from datetime import datetime, timezone
import vcon

logger = logging.getLogger(__name__)

class VconBuilder:
    def __init__(self, session_id: int, cohort_id: int):
        self.vcon = vcon.Vcon.build_new() # Create a new standard vcon object
        self.vcon.vcon_dict["vcon"] = "0.0.1" # Standardized version string
        self.session_id = session_id
        self.cohort_id = cohort_id
        
        # Add foundational metadata
        self._initialize_metadata()
        
    @classmethod
    def from_json(cls, vcon_json: str, session_id: int, cohort_id: int):
        """Reconstruct a VconBuilder from an existing JSON string"""
        instance = cls.__new__(cls)
        instance.session_id = session_id
        instance.cohort_id = cohort_id
        instance.vcon = vcon.Vcon()
        instance.vcon.vcon_dict = json.loads(vcon_json)
        return instance
        
    def _initialize_metadata(self):
        """Set standard metadata for the session vCon"""
        self.vcon.add_attachment(
            body={"session_id": self.session_id, "cohort_id": self.cohort_id},
            type="application/json",
            encoding="none"
        )
        
    def add_recording(self, file_path: str, url: str):
        """Append the primary media to the vCon"""
        # In a generic design, we either embed the file base64 or attach a link.
        # Since these are Zoom recordings (potentially large), we add a URL reference.
        from vcon.dialog import Dialog
        dialog = Dialog(
            type="recording",
            start=datetime.now(timezone.utc).isoformat(),
            parties=[0, 1], # Mock parties
            url=url,
            mimetype="video/mp4",
            filename=file_path.split("/")[-1]
        )
        self.vcon.add_dialog(dialog)
        
    def add_analysis(self, analysis_type: str, result: dict, vendor: str = "internal"):
        """Append an AI analysis payload (e.g. transcript, coaching feedback)"""
        self.vcon.add_analysis(
            type=analysis_type,
            dialog=[0],
            vendor=vendor,
            body=result,
            encoding="json"
        )
        
    def serialize(self) -> str:
        """Returns the vCon as a JSON string"""
        return self.vcon.dumps()
