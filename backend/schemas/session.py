from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class MessageBase(BaseModel):
    role: str
    content_type: str
    text_content: Optional[str] = None
    json_data: Optional[Dict[str, Any]] = None
    audio_path: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None

class MessageCreate(MessageBase):
    session_id: str

class MessageResponse(MessageBase):
    id: str
    session_id: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class SessionBase(BaseModel):
    title: str = "New Chat"

class SessionCreate(SessionBase):
    pass

class SessionUpdate(BaseModel):
    title: str

class SessionResponse(SessionBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    is_archived: bool
    metadata_json: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(from_attributes=True)

class SessionWithMessages(SessionResponse):
    messages: List[MessageResponse] = []
