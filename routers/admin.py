"""
Admin Router - AI Nurse Florence
Administrative endpoints for configuration management
"""

import os
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from utils.config import settings
from utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={
        200: {"description": "Operation successful"},
        403: {"description": "Forbidden - Admin access required"},
        500: {"description": "Internal server error"},
    },
)


class LiveDataToggleRequest(BaseModel):
    """Request model for toggling live data"""
    enabled: bool


class LiveDataToggleResponse(BaseModel):
    """Response model for live data toggle status"""
    live_data_enabled: bool
    message: str
    services_status: Dict[str, Any]


@router.get(
    "/live-data-status",
    response_model=LiveDataToggleResponse,
    summary="Get live data status",
    description="Check if live data services are currently enabled.",
)
async def get_live_data_status() -> LiveDataToggleResponse:
    """
    Get the current status of live data services.

    Returns:
        Current live data configuration and service status
    """
    try:
        # Check current configuration
        live_enabled = getattr(settings, 'USE_LIVE', False)

        # Get service status
        services_status = {
            "mydisease": getattr(settings, 'USE_MYDISEASE', True),
            "pubmed": getattr(settings, 'USE_PUBMED', True),
            "medlineplus": getattr(settings, 'USE_MEDLINEPLUS', True),
            "openai": bool(getattr(settings, 'OPENAI_API_KEY', None)),
        }

        return LiveDataToggleResponse(
            live_data_enabled=live_enabled,
            message=f"Live data is currently {'enabled' if live_enabled else 'disabled'}",
            services_status=services_status
        )
    except Exception as e:
        logger.error(f"Error getting live data status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get live data status"
        )


@router.post(
    "/toggle-live-data",
    response_model=LiveDataToggleResponse,
    summary="Toggle live data services",
    description="Enable or disable live external API services. When disabled, uses stub data.",
)
async def toggle_live_data(request: LiveDataToggleRequest) -> LiveDataToggleResponse:
    """
    Toggle live data services on/off.

    When live data is enabled, the system uses real external APIs.
    When disabled, it uses cached/stub data for demonstration purposes.

    Args:
        request: Request containing the desired enabled state

    Returns:
        Updated configuration status
    """
    try:
        # Update the runtime setting
        # Note: This is a runtime change and won't persist across restarts
        # For persistent changes, you'd need to update the .env file
        settings.USE_LIVE = request.enabled

        # Also update related service flags
        if hasattr(settings, 'USE_LIVE_SERVICES'):
            settings.USE_LIVE_SERVICES = request.enabled
        if hasattr(settings, 'USE_LIVE_APIS'):
            settings.USE_LIVE_APIS = request.enabled

        # Log the change
        logger.info(f"Live data services {'enabled' if request.enabled else 'disabled'} via admin toggle")

        # Get updated service status
        services_status = {
            "mydisease": getattr(settings, 'USE_MYDISEASE', True),
            "pubmed": getattr(settings, 'USE_PUBMED', True),
            "medlineplus": getattr(settings, 'USE_MEDLINEPLUS', True),
            "openai": bool(getattr(settings, 'OPENAI_API_KEY', None)),
            "live_mode": request.enabled
        }

        message = (
            f"Live data services {'enabled' if request.enabled else 'disabled'}. "
            f"{'Real external APIs will be used' if request.enabled else 'Stub data will be used for demonstration'}."
        )

        return LiveDataToggleResponse(
            live_data_enabled=request.enabled,
            message=message,
            services_status=services_status
        )

    except Exception as e:
        logger.error(f"Error toggling live data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle live data: {str(e)}"
        )


@router.get(
    "/config",
    summary="Get current configuration",
    description="Get current system configuration settings (non-sensitive only).",
)
async def get_config() -> Dict[str, Any]:
    """
    Get current system configuration.

    Returns non-sensitive configuration values for admin review.
    """
    try:
        config_info = {
            "app": {
                "name": getattr(settings, 'APP_NAME', 'AI Nurse Florence'),
                "version": getattr(settings, 'APP_VERSION', '2.1.0'),
                "environment": os.getenv('RAILWAY_ENVIRONMENT', 'development'),
            },
            "services": {
                "live_data": getattr(settings, 'USE_LIVE', False),
                "mydisease": getattr(settings, 'USE_MYDISEASE', True),
                "pubmed": getattr(settings, 'USE_PUBMED', True),
                "medlineplus": getattr(settings, 'USE_MEDLINEPLUS', True),
                "caching_enabled": getattr(settings, 'ENABLE_CACHING', True),
                "rate_limiting": getattr(settings, 'RATE_LIMIT_ENABLED', True),
            },
            "features": {
                "debug_routes": getattr(settings, 'ENABLE_DEBUG_ROUTES', False),
                "docs_enabled": getattr(settings, 'ENABLE_DOCS', True),
                "metrics_enabled": getattr(settings, 'ENABLE_METRICS', False),
            },
            "security": {
                "cors_configured": bool(getattr(settings, 'CORS_ORIGINS', None)),
                "jwt_configured": bool(getattr(settings, 'JWT_SECRET_KEY', None)),
                "openai_configured": bool(getattr(settings, 'OPENAI_API_KEY', None)),
            }
        }

        return config_info

    except Exception as e:
        logger.error(f"Error getting configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get configuration"
        )
