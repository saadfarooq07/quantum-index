from typing import Dict
from pathlib import Path
import json

class IPNotice:
    """Manages intellectual property notices for quantum-enhanced features."""
    
    def __init__(self):
        self.notices = {
            "quantum_completion": "Protected by Q0rtex Quantum-Inspired Algorithms",
            "metal_acceleration": "Metal Acceleration Technology © 2024 Q0rtex Team",
            "reality_metrics": "Reality Metrics System - Patent Pending"
        }
        
    def get_notice(self, feature: str) -> str:
        """Get the IP notice for a specific feature."""
        return self.notices.get(feature, "© 2024 Q0rtex Team - All Rights Reserved")
        
    def add_notice(self, feature: str, notice: str):
        """Add a new IP notice."""
        self.notices[feature] = notice
        
    def get_all_notices(self) -> Dict[str, str]:
        """Get all IP notices."""
        return self.notices.copy()
        
    @staticmethod
    def show_license_notice():
        """Display the main license notice."""
        print("Q0rtex - Quantum-Enhanced Terminal Integration")
        print("Copyright (c) 2024 Q0rtex Team")
        print("All Rights Reserved")
        print("Protected by QETIL License")

