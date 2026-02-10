# routes.py
from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, status, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import AccessTokenBearer, RoleChecker
from src.db.models import Todo
from src.db.main import get_session
from .service import TodoService
from .schemas import TodoResponse, TodoCreate, TodoUpdate, TodoListResponse
from src.errors import TodoNotFound

todo_router = APIRouter()
todo_service = TodoService()
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(["admin", "user"]))


@todo_router.get(
    "/", response_model=List[TodoListResponse], dependencies=[role_checker]
)
async def get_all_todos(
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(access_token_bearer),
):
    """Get all todos (admin only - typically you'd restrict this)"""
    todos = await todo_service.get_all_todos(session)
    return todos


@todo_router.get(
    "/user/{user_uid}", response_model=List[TodoResponse], dependencies=[role_checker]
)
async def get_user_todos(
    user_uid: uuid.UUID,
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(access_token_bearer),
):
    """Get all todos for a specific user, optionally filtered by completion status"""
    todos = await todo_service.get_user_todos(user_uid, session, completed)
    return todos


@todo_router.get(
    "/my-todos", response_model=List[TodoResponse], dependencies=[role_checker]
)
async def get_my_todos(
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    """Get todos for the currently authenticated user"""
    user_id = token_details.get("user")["user_uid"]
    todos = await todo_service.get_user_todos(user_id, session, completed)
    return todos


@todo_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=TodoResponse,
    dependencies=[role_checker],
)
async def create_todo(
    todo_data: TodoCreate,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    """Create a new todo for the authenticated user"""
    user_id = token_details.get("user")["user_uid"]
    new_todo = await todo_service.create_todo(todo_data, user_id, session)
    return new_todo


@todo_router.get(
    "/{todo_uid}", response_model=TodoResponse, dependencies=[role_checker]
)
async def get_todo(
    todo_uid: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(access_token_bearer),
):
    """Get a specific todo by ID"""
    todo = await todo_service.get_todo(todo_uid, session)

    if todo:
        return todo
    else:
        raise TodoNotFound()


@todo_router.patch(
    "/{todo_uid}", response_model=TodoResponse, dependencies=[role_checker]
)
async def update_todo(
    todo_uid: uuid.UUID,
    todo_update_data: TodoUpdate,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(access_token_bearer),
):
    """Update a todo (partial updates supported)"""
    updated_todo = await todo_service.update_todo(todo_uid, todo_update_data, session)

    if updated_todo is None:
        raise TodoNotFound()
    else:
        return updated_todo


@todo_router.post(
    "/{todo_uid}/toggle", response_model=TodoResponse, dependencies=[role_checker]
)
async def toggle_todo_completion(
    todo_uid: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(access_token_bearer),
):
    """Toggle the completion status of a todo (quick complete/uncomplete)"""
    todo = await todo_service.toggle_todo_completion(todo_uid, session)

    if todo is None:
        raise TodoNotFound()
    else:
        return todo


@todo_router.delete(
    "/{todo_uid}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[role_checker]
)
async def delete_todo(
    todo_uid: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(access_token_bearer),
):
    """Delete a todo"""
    todo_to_delete = await todo_service.delete_todo(todo_uid, session)

    if todo_to_delete is None:
        raise TodoNotFound()
    else:
        return None  # 204 No Content
