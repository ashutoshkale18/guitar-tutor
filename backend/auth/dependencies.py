# pyrefly: ignore [missing-import]
from fastapi import Depends, HTTPException, status
# pyrefly: ignore [missing-import]
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
# pyrefly: ignore [missing-import]
from sqlalchemy.ext.asyncio import AsyncSession
# pyrefly: ignore [missing-import]
from sqlalchemy.future import select

from database.engine import get_db
from database.models import User
from .security import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    
    if user is None:
        raise credentials_exception
        
    return user

import logging
logger = logging.getLogger(__name__)

async def get_ws_current_user(token: str, db: AsyncSession):
    """Authenticate WebSocket connections using a token query parameter."""
    # pyrefly: ignore [missing-import]
    from fastapi import WebSocketException
    
    if not token:
        logger.error("WS Auth Debug: Missing token")
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Missing token")
        
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
    except JWTError as e:
        logger.error(f"WS Auth Debug: JWTError {e}")
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    
    if user is None:
        logger.error(f"WS Auth Debug: User {user_id} not found")
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="User not found")
        
    return user
