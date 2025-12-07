"""
Integration Tests for Task Management API
Tests API endpoints with actual HTTP requests
"""

import sys
import os

import pytest
from fastapi.testclient import TestClient

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client"""
    return TestClient(app)


class TestRootEndpoints:
    """Test root and health endpoints"""

    def test_root_endpoint(self, client: TestClient) -> None:
        """Test root endpoint returns API info"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "1.0.0"

    def test_health_endpoint(self, client: TestClient) -> None:
        """Test health check endpoint"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "database" in data

    def test_docs_available(self, client: TestClient) -> None:
        """Test API documentation is available"""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_metrics_endpoint(self, client: TestClient) -> None:
        """Test Prometheus metrics endpoint"""
        response = client.get("/metrics")

        assert response.status_code == 200
        assert "http_requests_total" in response.text


class TestTaskEndpoints:
    """Test task CRUD endpoints"""

    def test_get_all_tasks(self, client: TestClient) -> None:
        """Test getting all tasks"""
        response = client.get("/tasks")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_task(self, client: TestClient) -> None:
        """Test creating a new task"""
        task_data = {
            "title": "Integration Test Task",
            "description": "Created during integration testing",
            "priority": "high"
        }

        response = client.post("/tasks", json=task_data)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["description"] == task_data["description"]
        assert data["priority"] == task_data["priority"]
        assert data["completed"] is False
        assert "id" in data

    def test_create_task_minimal(self, client: TestClient) -> None:
        """Test creating task with minimal data"""
        task_data = {"title": "Minimal Task"}

        response = client.post("/tasks", json=task_data)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Minimal Task"
        assert data["priority"] == "medium"  # Default

    def test_create_task_invalid_priority(self, client: TestClient) -> None:
        """Test creating task with invalid priority"""
        task_data = {
            "title": "Invalid Priority",
            "priority": "super-urgent"  # Invalid
        }

        response = client.post("/tasks", json=task_data)

        assert response.status_code == 422  # Validation error

    def test_create_task_empty_title(self, client: TestClient) -> None:
        """Test creating task with empty title"""
        task_data = {"title": ""}

        response = client.post("/tasks", json=task_data)

        assert response.status_code == 422  # Validation error

    def test_get_specific_task(self, client: TestClient) -> None:
        """Test getting a specific task"""
        # First create a task
        create_response = client.post("/tasks", json={"title": "Specific Task"})
        task_id = create_response.json()["id"]

        # Then get it
        response = client.get(f"/tasks/{task_id}")

        assert response.status_code == 200
        assert response.json()["title"] == "Specific Task"

    def test_get_nonexistent_task(self, client: TestClient) -> None:
        """Test getting a task that doesn't exist"""
        response = client.get("/tasks/99999")

        assert response.status_code == 404

    def test_update_task(self, client: TestClient) -> None:
        """Test updating a task"""
        # Create task
        create_response = client.post("/tasks", json={"title": "To Update"})
        task_id = create_response.json()["id"]

        # Update it
        update_data = {
            "title": "Updated Title",
            "completed": True
        }
        response = client.put(f"/tasks/{task_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["completed"] is True

    def test_update_nonexistent_task(self, client: TestClient) -> None:
        """Test updating a task that doesn't exist"""
        response = client.put("/tasks/99999", json={"title": "Updated"})

        assert response.status_code == 404

    def test_delete_task(self, client: TestClient) -> None:
        """Test deleting a task"""
        # Create task
        create_response = client.post("/tasks", json={"title": "To Delete"})
        task_id = create_response.json()["id"]

        # Delete it
        response = client.delete(f"/tasks/{task_id}")

        assert response.status_code == 204

        # Verify it's gone
        get_response = client.get(f"/tasks/{task_id}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_task(self, client: TestClient) -> None:
        """Test deleting a task that doesn't exist"""
        response = client.delete("/tasks/99999")

        assert response.status_code == 404

    def test_get_tasks_with_filters(self, client: TestClient) -> None:
        """Test filtering tasks"""
        # Create tasks with different priorities
        client.post("/tasks", json={"title": "High Priority", "priority": "high"})
        client.post("/tasks", json={"title": "Low Priority", "priority": "low"})

        # Filter by priority
        response = client.get("/tasks?priority=high")

        assert response.status_code == 200
        tasks = response.json()
        # At least one should be high priority
        high_priority = [t for t in tasks if t["priority"] == "high"]
        assert len(high_priority) > 0

    def test_get_tasks_with_pagination(self, client: TestClient) -> None:
        """Test paginating tasks"""
        response = client.get("/tasks?skip=0&limit=2")

        assert response.status_code == 200


class TestStatistics:
    """Test statistics endpoint"""

    def test_get_stats(self, client: TestClient) -> None:
        """Test getting task statistics"""
        response = client.get("/tasks/stats/summary")

        assert response.status_code == 200
        data = response.json()
        assert "total_tasks" in data
        assert "completed_tasks" in data
        assert "pending_tasks" in data
        assert "completion_rate" in data
        assert "by_priority" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
