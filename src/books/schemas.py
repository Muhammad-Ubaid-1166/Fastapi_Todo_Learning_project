# schemas.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid


# Base schema with common fields
class TodoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Todo title")
    detail: Optional[str] = Field(None, description="Todo details/description")
    due_date: Optional[datetime] = Field(None, description="When the todo is due")


# Schema for creating a new todo
class TodoCreate(TodoBase):
    pass  # Inherits title, detail, due_date from TodoBase


# Schema for updating an existing todo (all fields optional for partial updates)
class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    detail: Optional[str] = None
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None


# Schema for API responses (what users get back)
class TodoResponse(TodoBase):
    uid: uuid.UUID
    completed: bool
    user_uid: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # Allows conversion from SQLModel to Pydantic


# Optional: Schema for listing todos (minimal info)
class TodoListResponse(BaseModel):
    uid: uuid.UUID
    title: str
    completed: bool
    due_date: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True