"""
Core authentication logic using OAuth2 and JWT.

This module provides the functions and dependencies for handling the OAuth2
"Authorization Code" flow required by the GPT Store. It manages the creation
and verification of JSON Web Tokens (JWTs) to secure API endpoints.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from utils.config import settings
from database import get_db
from models import schemas as models_schemas
from models import user as models_user
from crud import user as crud_user
from utils.logging import get_logger

logger = get_logger(__name__)

# This dependency will look for a token in the "Authorization" header
# with the value "Bearer <token>". The tokenUrl is the endpoint that
# the client (our GPT) will use to get the token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

# --- JWT Creation ---

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Creates a new JSON Web Token (JWT)."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

# --- User Verification and Dependency ---

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_db)
) -> models_user.User:
    """
    A dependency to get the current user from a JWT.
    
    This function is used to protect API endpoints. It decodes the token,
    extracts the user ID, and fetches the user from the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        provider_user_id: str | None = payload.get("sub")
        if provider_user_id is None:
            raise credentials_exception
        token_data = models_schemas.TokenData(provider_user_id=provider_user_id)
    except JWTError:
        raise credentials_exception
    
    user = await crud_user.get_user_by_provider_id(db, provider="openai", provider_user_id=token_data.provider_user_id)
    if user is None:
        # This case should ideally not happen if the token was issued correctly.
        # It might indicate a deleted user.
        raise credentials_exception
    return user

# --- OpenAI OAuth2 Flow ---

async def exchange_code_for_openai_token(code: str) -> dict:
    """
    Exchanges an authorization code for an access token from OpenAI.
    This is the first part of the OAuth2 flow.
    """
    token_url = "https://auth.openai.com/oauth/token"
    payload = {
        "client_id": settings.OAUTH_CLIENT_ID,
        "client_secret": settings.OAUTH_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": "https://chat.openai.com/aip/g-YOUR_GPT_ID/oauth/callback" # This needs to be configured in your GPT
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=payload)
        if response.status_code != 200:
            logger.error(f"Failed to exchange code for OpenAI token: {response.text}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not exchange authorization code for token with OpenAI."
            )
        return response.json()

async def get_openai_user_info(openai_token: str) -> dict:
    """
    Fetches the user's profile information from OpenAI using their token.
    This gives us the unique, anonymous user ID.
    """
    user_info_url = "https://api.openai.com/v1/user"
    headers = {"Authorization": f"Bearer {openai_token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(user_info_url, headers=headers)
        if response.status_code != 200:
            logger.error(f"Failed to get user info from OpenAI: {response.text}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not retrieve user information from OpenAI."
            )
        return response.json()
