from pydantic import BaseModel
from typing import List, Optional

class TaskCreate(BaseModel):
    title: str 
    description: Optional[str] = None

class TaskRegistrationResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool
    created_by: str 
    message: str

class ErrorResponse(BaseModel):
    detail: str
    
class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    created_by: str
    completed: bool
    created_at: str 
    updated_at: str 

# class GetTasksResponse(BaseModel):
#     tasks: List[TaskResponse]

class GetTasksResponse(BaseModel):
    tasks: List[TaskResponse]
    total: int
    limit: int
    offset: int

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
