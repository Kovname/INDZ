"""
Database module - In-memory database for demo purposes
In production, replace with PostgreSQL/MySQL
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from threading import Lock


class Database:
    """Thread-safe in-memory database"""
    
    def __init__(self):
        self._tasks: Dict[int, dict] = {}
        self._counter = 0
        self._lock = Lock()
        self._connected = True
        
        # Add some demo data
        self._init_demo_data()
    
    def _init_demo_data(self):
        """Initialize with demo tasks"""
        demo_tasks = [
            {"title": "Setup CI Pipeline", "description": "Configure GitHub Actions", "priority": "high"},
            {"title": "Write Unit Tests", "description": "Add pytest tests", "priority": "high"},
            {"title": "Docker Configuration", "description": "Create Dockerfile", "priority": "medium"},
            {"title": "Documentation", "description": "Write API docs", "priority": "low"},
        ]
        
        for task_data in demo_tasks:
            from pydantic import BaseModel
            
            class TempTask(BaseModel):
                title: str
                description: Optional[str] = None
                priority: str = "medium"
            
            self.create_task(TempTask(**task_data))
    
    def is_connected(self) -> bool:
        """Check database connection status"""
        return self._connected
    
    def get_tasks(
        self,
        skip: int = 0,
        limit: int = 100,
        completed: Optional[bool] = None,
        priority: Optional[str] = None
    ) -> List[dict]:
        """Get all tasks with filtering"""
        with self._lock:
            tasks = list(self._tasks.values())
            
            # Apply filters
            if completed is not None:
                tasks = [t for t in tasks if t["completed"] == completed]
            if priority:
                tasks = [t for t in tasks if t["priority"] == priority]
            
            # Apply pagination
            return tasks[skip:skip + limit]
    
    def get_task(self, task_id: int) -> Optional[dict]:
        """Get a specific task"""
        with self._lock:
            return self._tasks.get(task_id)
    
    def create_task(self, task_data) -> dict:
        """Create a new task"""
        with self._lock:
            self._counter += 1
            now = datetime.utcnow()
            
            task = {
                "id": self._counter,
                "title": task_data.title,
                "description": task_data.description,
                "priority": task_data.priority,
                "completed": False,
                "created_at": now,
                "updated_at": now
            }
            
            self._tasks[self._counter] = task
            return task
    
    def update_task(self, task_id: int, task_update) -> Optional[dict]:
        """Update an existing task"""
        with self._lock:
            if task_id not in self._tasks:
                return None
            
            task = self._tasks[task_id]
            update_data = task_update.model_dump(exclude_unset=True)
            
            for field, value in update_data.items():
                if value is not None:
                    task[field] = value
            
            task["updated_at"] = datetime.utcnow()
            return task
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task"""
        with self._lock:
            if task_id not in self._tasks:
                return False
            del self._tasks[task_id]
            return True
    
    def get_stats(self) -> dict:
        """Get task statistics"""
        with self._lock:
            tasks = list(self._tasks.values())
            total = len(tasks)
            completed = sum(1 for t in tasks if t["completed"])
            
            priority_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
            for task in tasks:
                priority_counts[task["priority"]] += 1
            
            return {
                "total_tasks": total,
                "completed_tasks": completed,
                "pending_tasks": total - completed,
                "completion_rate": round(completed / total * 100, 2) if total > 0 else 0,
                "by_priority": priority_counts
            }
