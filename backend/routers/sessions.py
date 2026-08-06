from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
import logging
import os

from config import STATIC_DIR
from database.engine import get_db
from database.models import User, Session, Message
from auth.dependencies import get_current_user
from schemas.session import SessionResponse, SessionCreate, SessionUpdate, SessionWithMessages, MessageResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/sessions",
    tags=["sessions"]
)

@router.get("", response_model=List[SessionResponse])
async def get_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all sessions for the current user."""
    query = select(Session).where(Session.user_id == current_user.id).order_by(Session.updated_at.desc())
    result = await db.execute(query)
    sessions = result.scalars().all()
    return sessions

@router.post("", response_model=SessionResponse)
async def create_session(
    session_data: SessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new chat session."""
    db_session = Session(
        user_id=current_user.id,
        title=session_data.title
    )
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)
    return db_session

@router.get("/{session_id}", response_model=SessionWithMessages)
async def get_session_with_messages(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific session with all its messages."""
    # Verify session belongs to user
    query = select(Session).where(Session.id == session_id, Session.user_id == current_user.id)
    result = await db.execute(query)
    session = result.scalars().first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    # Get messages
    msg_query = select(Message).where(Message.session_id == session_id).order_by(Message.created_at.asc())
    msg_result = await db.execute(msg_query)
    messages = msg_result.scalars().all()
    
    # We construct a response object that matches the SessionWithMessages schema
    session_dict = {
        "id": session.id,
        "title": session.title,
        "user_id": session.user_id,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "is_archived": session.is_archived,
        "metadata_json": session.metadata_json,
        "messages": messages
    }
    
    return session_dict

@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: str,
    session_data: SessionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a session (e.g. rename title)."""
    query = select(Session).where(Session.id == session_id, Session.user_id == current_user.id)
    result = await db.execute(query)
    session = result.scalars().first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    session.title = session_data.title
    await db.commit()
    await db.refresh(session)
    return session

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a session."""
    query = select(Session).where(Session.id == session_id, Session.user_id == current_user.id)
    result = await db.execute(query)
    session = result.scalars().first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    await db.delete(session)
    await db.commit()
    return None

@router.get("/audio/{filename}")
async def get_audio_file(filename: str):
    """Serve a generated TTS audio file."""
    # Prevent directory traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
        
    file_path = STATIC_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
        
    return FileResponse(file_path, media_type="audio/wav")
