from datetime import timedelta
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlmodel import Session, select
from ..schemas.task_schemas import ( TaskRegistrationResponse, TaskCreate, TaskUpdate, 
    GetTasksResponse, TaskResponse)
from ..exceptions.user_exception import *
from ..exceptions.task_exception import *
from ..models.user_model import User
from ..models.task_model import Task
from ..jwt_auth.token_validation import JWTBearer
from ..database import get_session
from cache import redis_client

router = APIRouter(tags=["ToDo_List"])

def get_user_from_token(token_payload: dict, session: Session):
    user_id = token_payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access.")
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user

@router.post("/tasks", response_model=TaskRegistrationResponse)
def create_task(
    task: TaskCreate,
    session: Session = Depends(get_session),
    token_payload: dict = Depends(JWTBearer())
):
    try:
        if not task.title:
            raise TitleIsMandatory()
        if len(task.title) > 100:
            raise TitleLengthExceed()
        user = get_user_from_token(token_payload, session)
        existing_task = session.exec(select(Task).where(Task.title == task.title)).first()
        if existing_task:
            raise TaskAlreadyExists()
        
        new_task = Task(
            title=task.title,
            description=task.description,
            created_by=user.username,
            completed=False
        )
        session.add(new_task)
        session.commit()
        session.refresh(new_task)
        # Store task in Redis for 10 minutes
        task_data = {
            "id": str(new_task.id),
            "title": new_task.title,
            "description": new_task.description,
            "created_by": new_task.created_by,
            "completed": new_task.completed,
            "created_at": new_task.created_at.isoformat(),
            "updated_at": new_task.updated_at.isoformat(),
        }
        redis_client.setex(f"task:{new_task.id}", timedelta(minutes=10), json.dumps(task_data))
        return TaskRegistrationResponse(
            id=new_task.id, # type: ignore
            title=new_task.title,
            description=new_task.description,
            created_by=new_task.created_by,
            completed=new_task.completed,
            message="Task created successfully."
        )
    except Exception as e:
        raise DatabaseError()

# @router.get('/tasks', response_model=GetTasksResponse)
# def get_tasks(
#     token_payload: dict = Depends(JWTBearer()),
#     session: Session = Depends(get_session)
# ):
#     try:
#         tasks = session.exec(select(Task)).all()
#         if not tasks:
#             raise TaskNotFound()
#         task_list = [
#             {
#                 "id": str(task.id),
#                 "title": task.title,
#                 "description": task.description,
#                 "created_by": task.created_by,
#                 "completed": task.completed,
#                 "created_at": task.created_at.isoformat(),
#                 "updated_at": task.updated_at.isoformat()
#             }
#             for task in tasks
#         ]
#         return GetTasksResponse(tasks=task_list) # type: ignore
#     except Exception as e:
#         raise GeneralError(message=f"Unexpected error: {str(e)}")

@router.get('/tasks/{id}', response_model=TaskResponse)
def get_task_by_id(
    id: int,
    session: Session = Depends(get_session),
    token_payload: dict = Depends(JWTBearer())
):
    try:
        cached_task = redis_client.get(f"task:{id}")
        if cached_task:
            return TaskResponse(**json.loads(cached_task)) # type: ignore
        task = session.exec(select(Task).where(Task.id == id)).first()
        if not task:
            raise TaskNotFound()
        task_data = {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "created_by": task.created_by,
            "completed": task.completed,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
        }
        # Store in Redis for future requests
        redis_client.setex(f"task:{id}", timedelta(minutes=10), json.dumps(task_data))
        return TaskResponse(**task_data)
    except Exception as e:
        raise GeneralError(message=f"Unexpected error: {str(e)}")

@router.patch('/tasks/{id}', response_model=TaskResponse)
def partial_update_task(
    id: int,
    task_update: TaskUpdate,
    session: Session = Depends(get_session),
    token_payload: dict = Depends(JWTBearer())
):
    try:
        user = get_user_from_token(token_payload, session)
        task_to_update = session.exec(select(Task).where(Task.id == id)).first()
        if not task_to_update:
            raise TaskNotFound()
        if task_to_update.created_by != user.username:
            raise UnauthorizedAccess()
        if task_update.title and len(task_update.title) > 100:
            raise TitleLengthExceed()
        # Update only the provided fields
        task_to_update.title = task_update.title if task_update.title else task_to_update.title
        task_to_update.description = task_update.description if task_update.description else task_to_update.description
        if task_update.completed is not None:
            task_to_update.completed = task_update.completed
        session.commit()
        session.refresh(task_to_update)
        updated_task_data = {
            "id": str(task_to_update.id),
            "title": task_to_update.title,
            "description": task_to_update.description,
            "created_by": task_to_update.created_by,
            "completed": task_to_update.completed,
            "created_at": task_to_update.created_at.isoformat(),
            "updated_at": task_to_update.updated_at.isoformat(),
        }

        redis_client.delete(f"task:{id}")
        return TaskResponse(**updated_task_data)

    except Exception as e:
        raise GeneralError(message=f"Unexpected error: {str(e)}")

@router.delete('/tasks/{id}', response_model=TaskResponse)
def delete_task(
    id: int,
    session: Session = Depends(get_session),
    token_payload: dict = Depends(JWTBearer())
):
    try:
        user = get_user_from_token(token_payload, session)
        task_to_delete = session.exec(select(Task).where(Task.id == id)).first()
        if not task_to_delete:
            raise TaskNotFound()
        if task_to_delete.created_by != user.username:
            raise UnauthorizedAccess()
        session.delete(task_to_delete)
        session.commit()
        redis_client.delete(f"task:{id}")  # Invalidate cache
        return TaskResponse(
            id=str(task_to_delete.id), # type: ignore
            title=task_to_delete.title,
            description=task_to_delete.description,
            created_by=task_to_delete.created_by,
            completed=task_to_delete.completed,
            created_at=task_to_delete.created_at.isoformat(),
            updated_at=task_to_delete.updated_at.isoformat()
        )
    except Exception as e:
        raise GeneralError(message=f"Unexpected error: {str(e)}")


@router.get('/tasks', response_model=GetTasksResponse)
def get_tasks(
    token_payload: dict = Depends(JWTBearer()),
    session: Session = Depends(get_session),
    limit: int = 10,  # Default page size
    offset: int = 0   # Default starting point
):
    try:
        cache_key = f"tasks:limit={limit}:offset={offset}"
        cached_data = redis_client.get(cache_key)

        if cached_data:
            # Return cached data if it exists
            return json.loads(cached_data) # type: ignore

        tasks_query = select(Task).offset(offset).limit(limit)
        tasks = session.exec(tasks_query).all()

        if not tasks:
            raise TaskNotFound()

        task_list = [
            TaskResponse(
                id=str(task.id), # type: ignore
                title=task.title,
                description=task.description,
                created_by=task.created_by,
                completed=task.completed,
                created_at=task.created_at.isoformat(),
                updated_at=task.updated_at.isoformat()
            )
            for task in tasks
        ]

        total_tasks = session.exec(select(func.count()).select_from(Task)).one()  # Count total tasks

        # Create response data
        response_data = GetTasksResponse(
            tasks=task_list,
            total=total_tasks,
            limit=limit,
            offset=offset
        )

        # Cache the response for 10 minutes
        redis_client.setex(cache_key, timedelta(minutes=10), json.dumps(response_data.dict()))

        return response_data

    except Exception as e:
        raise GeneralError(message=f"Unexpected error: {str(e)}")








