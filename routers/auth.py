"""
Authentication router for handling the OAuth2 flow.

This module provides the `/token` endpoint required by the GPT Store's
OAuth2 "Authorization Code" flow. When a user authorizes the GPT, OpenAI
sends a code to this endpoint, which we exchange for an access token.
"""

from datetime import timedelta

from crud import user as crud_user
from database import get_db
from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from models import schemas as models_schemas
from utils import auth as auth_utils
from utils.config import settings
from utils.logging import get_logger

router = APIRouter(prefix="/auth", tags=["authentication"])
logger = get_logger(__name__)


@router.post("/token", response_model=models_schemas.Token)
async def login_for_access_token(
    code: str = Form(...), db: AsyncSession = Depends(get_db)
):
    """
    The OAuth2 token endpoint.

    OpenAI will call this endpoint with an authorization code. We exchange
    that code for an OpenAI access token, fetch the user's OpenAI ID,
    find or create a corresponding user in our database, and then issue
    our own JWT access token back to the client (the GPT).
    """
    if not settings.OAUTH_CLIENT_ID or not settings.OAUTH_CLIENT_SECRET:
        logger.error("OAuth2 Client ID or Secret not configured.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication system is not configured.",
        )

    # Step 1: Exchange the authorization code for an OpenAI access token
    try:
        openai_token_data = await auth_utils.exchange_code_for_openai_token(code)
        openai_access_token = openai_token_data.get("access_token")
        if not openai_access_token:
            raise HTTPException(
                status_code=400, detail="OpenAI did not return an access token."
            )
    except HTTPException as e:
        logger.error(f"Failed during code exchange with OpenAI: {e.detail}")
        raise  # Reraise the exception to return the error to the client

    # Step 2: Use the OpenAI token to get the user's info (especially their unique ID)
    try:
        openai_user_info = await auth_utils.get_openai_user_info(openai_access_token)
        provider_user_id = openai_user_info.get("id")
        if not provider_user_id:
            raise HTTPException(
                status_code=400, detail="OpenAI did not return a user ID."
            )
    except HTTPException as e:
        logger.error(f"Failed to get user info from OpenAI: {e.detail}")
        raise

    # Step 3: Find the user in our database or create a new one
    user = await crud_user.get_user_by_provider_id(
        db, provider="openai", provider_user_id=provider_user_id
    )
    if not user:
        logger.info(f"Creating new user for OpenAI user ID: {provider_user_id}")
        user = await crud_user.create_user(
            db, provider="openai", provider_user_id=provider_user_id
        )

    # Step 4: Create our own JWT access token for the user
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_utils.create_access_token(
        data={"sub": user.provider_user_id}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
