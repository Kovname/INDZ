"""
FastAPI Application - Task Management API
A simple but fully-featured API for CI/CD demonstration
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uvicorn
import os

# Import our modules
from .database import Database
from .metrics import setup_metrics, track_request

# Initialize FastAPI app
app = FastAPI(
    title="Task Management API",
    description="A demo API for CI/CD pipeline demonstration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Prometheus metrics
setup_metrics(app)

# Database instance
db = Database()


# Pydantic Models
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Implement CI/CD",
                "description": "Setup GitHub Actions pipeline",
                "priority": "high"
            }
        }


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")
    completed: Optional[bool] = None


class Task(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: str
    completed: bool
    created_at: datetime
    updated_at: datetime


class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    version: str
    database: str


# API Endpoints
@app.get("/", tags=["Root"])
@track_request
async def root():
    """Root endpoint - API info"""
    return {
        "message": "Welcome to Task Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthCheck, tags=["Health"])
@track_request
async def health_check():
    """Health check endpoint for monitoring"""
    db_status = "connected" if db.is_connected() else "disconnected"
    return HealthCheck(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0",
        database=db_status
    )


@app.get("/tasks", response_model=List[Task], tags=["Tasks"])
@track_request
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    completed: Optional[bool] = None,
    priority: Optional[str] = None
):
    """Get all tasks with optional filtering"""
    return db.get_tasks(skip=skip, limit=limit, completed=completed, priority=priority)


@app.get("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
@track_request
async def get_task(task_id: int):
    """Get a specific task by ID"""
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    return task


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
@track_request
async def create_task(task: TaskCreate):
    """Create a new task"""
    return db.create_task(task)


@app.put("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
@track_request
async def update_task(task_id: int, task_update: TaskUpdate):
    """Update an existing task"""
    task = db.update_task(task_id, task_update)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tasks"])
@track_request
async def delete_task(task_id: int):
    """Delete a task"""
    success = db.delete_task(task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    return None


@app.get("/tasks/stats/summary", tags=["Statistics"])
@track_request
async def get_stats():
    """Get task statistics"""
    return db.get_stats()


# Run the application
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("ENV", "development") == "development"
    )
