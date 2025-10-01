"""
Application Configuration
Supports both standalone and Epic/EHR integrated deployment modes
"""

from enum import Enum
from pydantic_settings import BaseSettings
from typing import Optional
import os


class IntegrationMode(str, Enum):
    """EHR Integration Modes"""
    STANDALONE = "standalone"  # Current: No EHR connection, manual data entry
    EPIC_INTEGRATED = "epic_integrated"  # Future: Real-time Epic FHIR integration


class Settings(BaseSettings):
    """
    Application settings with Epic/EHR integration support

    Standalone Mode (Current):
    - Nurses manually enter patient data
    - Session-only storage (HIPAA-safe)
    - No external system connections

    Epic-Integrated Mode (Future):
    - Scan patient MRN → Auto-fetch from Epic FHIR API
    - Pre-populate forms with patient data
    - Write discharge notes back to Epic chart
    - Still session-only (no PHI persistence)
    """

    # ============================================================================
    # Integration Mode
    # ============================================================================
    integration_mode: IntegrationMode = IntegrationMode.STANDALONE

    # ============================================================================
    # Epic FHIR Configuration (Future Use)
    # ============================================================================

    # Epic FHIR Base URL
    epic_fhir_base_url: Optional[str] = None

    # OAuth 2.0 Credentials
    epic_client_id: Optional[str] = None
    epic_client_secret: Optional[str] = None
    epic_oauth_enabled: bool = False
    epic_oauth_token_url: Optional[str] = None
    epic_oauth_authorize_url: Optional[str] = None

    # Epic Application Configuration
    epic_app_name: str = "AI Nurse Florence"
    epic_app_version: str = "1.0.0"

    # Sandbox Mode (for development/testing with Epic sandbox)
    epic_sandbox_mode: bool = False
    epic_sandbox_url: str = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/"

    # FHIR Resource Endpoints (relative to base_url)
    fhir_patient_endpoint: str = "/Patient"
    fhir_encounter_endpoint: str = "/Encounter"
    fhir_condition_endpoint: str = "/Condition"
    fhir_medication_request_endpoint: str = "/MedicationRequest"
    fhir_document_reference_endpoint: str = "/DocumentReference"

    # Request timeout for Epic API calls (seconds)
    epic_request_timeout: int = 30

    # ============================================================================
    # Session Management (HIPAA Compliance)
    # ============================================================================

    # Patient data session TTL (time-to-live in seconds)
    patient_session_ttl: int = 7200  # 2 hours

    # Auto-cleanup interval (seconds)
    session_cleanup_interval: int = 300  # 5 minutes

    # ============================================================================
    # Database Configuration
    # ============================================================================

    database_url: str = "sqlite:///./ai_nurse_florence.db"

    # ============================================================================
    # API Configuration
    # ============================================================================

    api_v1_prefix: str = "/api/v1"
    project_name: str = "AI Nurse Florence"

    # ============================================================================
    # Security
    # ============================================================================

    secret_key: str = os.getenv("SECRET_KEY", "development-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # ============================================================================
    # Feature Flags
    # ============================================================================

    # Enable/disable Epic integration features in UI
    show_epic_integration_ui: bool = False

    # Enable MRN barcode scanning (requires Epic integration)
    enable_mrn_scanning: bool = False

    # Enable write-back to Epic chart
    enable_epic_write_back: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


# Helper functions
def is_epic_enabled() -> bool:
    """Check if Epic integration is enabled"""
    return settings.integration_mode == IntegrationMode.EPIC_INTEGRATED


def is_standalone_mode() -> bool:
    """Check if running in standalone mode"""
    return settings.integration_mode == IntegrationMode.STANDALONE


def get_epic_base_url() -> str:
    """Get Epic FHIR base URL (sandbox or production)"""
    if settings.epic_sandbox_mode:
        return settings.epic_sandbox_url
    return settings.epic_fhir_base_url or settings.epic_sandbox_url


def validate_epic_config() -> tuple[bool, list[str]]:
    """
    Validate Epic configuration

    Returns:
        (is_valid, list_of_errors)
    """
    if not is_epic_enabled():
        return True, []

    errors = []

    if not settings.epic_fhir_base_url and not settings.epic_sandbox_mode:
        errors.append("epic_fhir_base_url is required when Epic integration is enabled")

    if settings.epic_oauth_enabled:
        if not settings.epic_client_id:
            errors.append("epic_client_id is required when OAuth is enabled")
        if not settings.epic_client_secret:
            errors.append("epic_client_secret is required when OAuth is enabled")
        if not settings.epic_oauth_token_url:
            errors.append("epic_oauth_token_url is required when OAuth is enabled")

    return len(errors) == 0, errors
