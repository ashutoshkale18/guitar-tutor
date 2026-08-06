from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from database.engine import get_db
from auth.dependencies import get_current_user
from database.models import User
from services.memory_service import get_user_profile, update_user_preference

router = APIRouter()

@router.get("/me/memory")
async def get_my_memory(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the current user's profile and memory."""
    profile = await get_user_profile(current_user.id, db)
    return profile

@router.put("/me/memory")
async def update_my_memory(
    preferences: Dict[str, str],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user preferences."""
    for key, value in preferences.items():
        await update_user_preference(current_user.id, key, value, db)
    return {"status": "success"}
