from fastapi import FastAPI
from .routers import user_router as user_router
from .routers import task_router as task_router
from .database import engine, create_db_and_tables
from sqlmodel import SQLModel

app = FastAPI()

SQLModel.metadata.create_all(engine) # Create tables if they don't exist
app.include_router(user_router.router)
app.include_router(task_router.router)
@app.get("/")
async def root():
    return {"message": "Hello from the API!"}