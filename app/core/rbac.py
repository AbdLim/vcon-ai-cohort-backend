from pathlib import Path
from typing import Dict, Set
import yaml
from app.core.config import settings

class RBAC:
    def __init__(self, config_file: str = "roles.yaml"):
        # Assuming roles.yaml is in the project root
        self.config_file = Path(config_file)
        self.roles: Dict[str, Set[str]] = {}
        self._load_config()

    def _load_config(self):
        if not self.config_file.exists():
            # If not found, we could log a warning or default to empty
            # For now, let's assume valid setup or empty
            return
        
        try:
            with open(self.config_file, "r") as f:
                data = yaml.safe_load(f) or {}
                
            for role, perms in data.items():
                self.roles[role] = set(perms)
        except Exception as e:
            # Fallback for safety, maybe log error
            print(f"Error loading RBAC config: {e}")

    def has_permission(self, role: str, permission: str) -> bool:
        if role not in self.roles:
            return False
        
        perms = self.roles[role]
        if "*" in perms:
            return True
            
        return permission in perms

# Singleton instance
rbac = RBAC()
