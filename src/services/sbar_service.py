"""
SBAR Service - AI Nurse Florence
Following Service Layer Architecture for clinical documentation wizard
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from src.utils.config import get_settings
from src.utils.redis_cache import cached

logger = logging.getLogger(__name__)

class SBARService:
    """SBAR service following Service Layer Architecture."""
    
    def __init__(self):
        self.settings = get_settings()
        self.banner = self.settings.EDUCATIONAL_BANNER
        
    @cached(ttl_seconds=1800)
    async def get_sbar_template(self, specialty: str = "general") -> Dict[str, Any]:
        """Get SBAR template following Wizard Pattern Implementation."""
        templates = {
            "general": {
                "situation": {
                    "prompt": "Current patient situation and immediate concerns",
                    "example": "Patient presenting with chest pain, vital signs stable"
                },
                "background": {
                    "prompt": "Relevant medical history and context", 
                    "example": "65-year-old with history of hypertension, diabetes"
                },
                "assessment": {
                    "prompt": "Clinical assessment and current condition",
                    "example": "Possible cardiac etiology, EKG shows ST elevation"
                },
                "recommendation": {
                    "prompt": "Specific recommendations and next steps",
                    "example": "Recommend immediate cardiology consult"
                }
            }
        }
        
        return {
            "banner": self.banner,
            "specialty": specialty,
            "template": templates.get(specialty.lower(), templates["general"]),
            "timestamp": datetime.now().isoformat()
        }

def create_sbar_service() -> Optional[SBARService]:
    """Create SBAR service with graceful degradation."""
    try:
        return SBARService()
    except Exception as e:
        logger.warning(f"SBAR service unavailable: {e}")
        return None