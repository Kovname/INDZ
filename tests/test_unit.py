"""
Unit Tests for Task Management API
Tests individual components in isolation
"""

import pytest
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class MockTaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"


class MockTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    completed: Optional[bool] = None


# Import after mocks to avoid circular imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import Database


class TestDatabase:
    """Unit tests for Database class"""
    
    def setup_method(self):
        """Setup fresh database for each test"""
        self.db = Database()
        # Clear demo data
        self.db._tasks.clear()
        self.db._counter = 0
    
    def test_database_connection(self):
        """Test database connection status"""
        assert self.db.is_connected() is True
    
    def test_create_task(self):
        """Test task creation"""
        task_data = MockTaskCreate(
            title="Test Task",
            description="Test Description",
            priority="high"
        )
        
        task = self.db.create_task(task_data)
        
        assert task["id"] == 1
        assert task["title"] == "Test Task"
        assert task["description"] == "Test Description"
        assert task["priority"] == "high"
        assert task["completed"] is False
        assert isinstance(task["created_at"], datetime)
    
    def test_get_task(self):
        """Test getting a specific task"""
        task_data = MockTaskCreate(title="Get Task Test")
        created = self.db.create_task(task_data)
        
        task = self.db.get_task(created["id"])
        
        assert task is not None
        assert task["title"] == "Get Task Test"
    
    def test_get_nonexistent_task(self):
        """Test getting a task that doesn't exist"""
        task = self.db.get_task(9999)
        assert task is None
    
    def test_get_all_tasks(self):
        """Test getting all tasks"""
        self.db.create_task(MockTaskCreate(title="Task 1"))
        self.db.create_task(MockTaskCreate(title="Task 2"))
        self.db.create_task(MockTaskCreate(title="Task 3"))
        
        tasks = self.db.get_tasks()
        
        assert len(tasks) == 3
    
    def test_get_tasks_with_pagination(self):
        """Test pagination"""
        for i in range(10):
            self.db.create_task(MockTaskCreate(title=f"Task {i}"))
        
        tasks = self.db.get_tasks(skip=2, limit=3)
        
        assert len(tasks) == 3
        assert tasks[0]["title"] == "Task 2"
    
    def test_get_tasks_filter_by_priority(self):
        """Test filtering by priority"""
        self.db.create_task(MockTaskCreate(title="Low", priority="low"))
        self.db.create_task(MockTaskCreate(title="High", priority="high"))
        self.db.create_task(MockTaskCreate(title="High 2", priority="high"))
        
        tasks = self.db.get_tasks(priority="high")
        
        assert len(tasks) == 2
        assert all(t["priority"] == "high" for t in tasks)
    
    def test_update_task(self):
        """Test task update"""
        task_data = MockTaskCreate(title="Original Title")
        created = self.db.create_task(task_data)
        
        update = MockTaskUpdate(title="Updated Title", completed=True)
        updated = self.db.update_task(created["id"], update)
        
        assert updated["title"] == "Updated Title"
        assert updated["completed"] is True
    
    def test_update_nonexistent_task(self):
        """Test updating a task that doesn't exist"""
        update = MockTaskUpdate(title="Updated")
        result = self.db.update_task(9999, update)
        
        assert result is None
    
    def test_delete_task(self):
        """Test task deletion"""
        task_data = MockTaskCreate(title="To Delete")
        created = self.db.create_task(task_data)
        
        result = self.db.delete_task(created["id"])
        
        assert result is True
        assert self.db.get_task(created["id"]) is None
    
    def test_delete_nonexistent_task(self):
        """Test deleting a task that doesn't exist"""
        result = self.db.delete_task(9999)
        assert result is False
    
    def test_get_stats(self):
        """Test statistics generation"""
        self.db.create_task(MockTaskCreate(title="Task 1", priority="high"))
        self.db.create_task(MockTaskCreate(title="Task 2", priority="low"))
        task3 = self.db.create_task(MockTaskCreate(title="Task 3", priority="high"))
        
        # Mark one as completed
        self.db.update_task(task3["id"], MockTaskUpdate(completed=True))
        
        stats = self.db.get_stats()
        
        assert stats["total_tasks"] == 3
        assert stats["completed_tasks"] == 1
        assert stats["pending_tasks"] == 2
        assert stats["by_priority"]["high"] == 2
        assert stats["by_priority"]["low"] == 1


class TestTaskValidation:
    """Unit tests for task data validation"""
    
    def test_valid_task_creation(self):
        """Test valid task data"""
        task = MockTaskCreate(
            title="Valid Task",
            description="Valid description",
            priority="high"
        )
        assert task.title == "Valid Task"
    
    def test_task_with_default_priority(self):
        """Test default priority assignment"""
        task = MockTaskCreate(title="Default Priority Task")
        assert task.priority == "medium"
    
    def test_task_optional_description(self):
        """Test optional description"""
        task = MockTaskCreate(title="No Description")
        assert task.description is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
