"""
CRUD (Create, Read, Update, Delete) operations for the User model.

This module encapsulates the database logic for interacting with the 'users'
table, providing a clean and reusable interface for our services.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.user import User

async def get_user_by_provider_id(db: AsyncSession, provider: str, provider_user_id: str) -> User | None:
    """
    Retrieve a user from the database by their provider and provider_user_id.
    """
    result = await db.execute(
        select(User).filter_by(provider=provider, provider_user_id=provider_user_id)
    )
    return result.scalars().first()

async def create_user(db: AsyncSession, provider: str, provider_user_id: str) -> User:
    """
    Create a new user in the database.
    """
    new_user = User(provider=provider, provider_user_id=provider_user_id)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
