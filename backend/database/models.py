from sqlalchemy import Column, String, JSON, DateTime, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.sql import func
from .engine import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime, nullable=True)
    settings = Column(JSON, default={})

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), default="New Chat")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_archived = Column(Boolean, default=False)
    metadata_json = Column("metadata", JSON, default={})

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False) # 'user', 'assistant', 'system'
    content_type = Column(String(20), nullable=False) # 'text', 'audio', 'chords', 'notes', 'strumming'
    text_content = Column(String(10000), nullable=True)
    json_data = Column(JSON, nullable=True)
    audio_path = Column(String(512), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    metadata_json = Column("metadata", JSON, default={})

class UserMemory(Base):
    __tablename__ = "user_memory"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    memory_type = Column(String(50), nullable=False)
    key = Column(String(255), nullable=False)
    value = Column(String(10000), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('user_id', 'memory_type', 'key', name='_user_memory_uc'),
    )
