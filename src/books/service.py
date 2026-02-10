# service.py
from datetime import datetime
from typing import Optional
import uuid

from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.models import Todo
from .schemas import TodoCreate, TodoUpdate


class TodoService:
    """Service layer for Todo CRUD operations"""
    
    async def get_all_todos(self, session: AsyncSession):
        """Get all todos ordered by creation date (newest first)"""
        statement = select(Todo).order_by(desc(Todo.created_at))
        result = await session.execute(statement)
        return result.scalars().all()

    async def get_user_todos(
        self, 
        user_uid: uuid.UUID, 
        session: AsyncSession,
        completed: Optional[bool] = None
    ):
        """Get all todos for a specific user, optionally filtered by completion status"""
        statement = select(Todo).where(Todo.user_uid == user_uid)
        
        # Optional filter by completed status
        if completed is not None:
            statement = statement.where(Todo.completed == completed)
        
        statement = statement.order_by(desc(Todo.created_at))
        result = await session.execute(statement)
        return result.scalars().all()

    async def get_todo(self, todo_uid: uuid.UUID, session: AsyncSession):
        """Get a single todo by ID"""
        statement = select(Todo).where(Todo.uid == todo_uid)
        result = await session.execute(statement)
        todo = result.scalars().first()
        return todo if todo is not None else None

    async def create_todo(
        self, 
        todo_data: TodoCreate, 
        user_uid: uuid.UUID, 
        session: AsyncSession
    ):
        """Create a new todo for a user"""
        todo_data_dict = todo_data.model_dump()
        
        new_todo = Todo(**todo_data_dict)
        new_todo.user_uid = user_uid
        
        session.add(new_todo)
        await session.commit()
        await session.refresh(new_todo)  # Refresh to get generated fields
        
        return new_todo

    async def update_todo(
        self, 
        todo_uid: uuid.UUID, 
        update_data: TodoUpdate, 
        session: AsyncSession
    ):
        """Update an existing todo (partial updates supported)"""
        todo_to_update = await self.get_todo(todo_uid, session)
        
        if todo_to_update is None:
            return None
        
        # Only update fields that were actually provided
        update_data_dict = update_data.model_dump(exclude_unset=True)
        
        for key, value in update_data_dict.items():
            setattr(todo_to_update, key, value)
        
        # Update the updated_at timestamp
        todo_to_update.updated_at = datetime.now()
        
        await session.commit()
        await session.refresh(todo_to_update)
        
        return todo_to_update

    async def delete_todo(self, todo_uid: uuid.UUID, session: AsyncSession):
        """Delete a todo by ID"""
        todo_to_delete = await self.get_todo(todo_uid, session)
        
        if todo_to_delete is None:
            return None
        
        await session.delete(todo_to_delete)
        await session.commit()
        
        return {}  # Return empty dict to indicate successful deletion
    
    async def toggle_todo_completion(
        self, 
        todo_uid: uuid.UUID, 
        session: AsyncSession
    ):
        """Toggle the completed status of a todo"""
        todo = await self.get_todo(todo_uid, session)
        
        if todo is None:
            return None
        
        todo.completed = not todo.completed
        todo.updated_at = datetime.now()
        
        await session.commit()
        await session.refresh(todo)
        
        return todo