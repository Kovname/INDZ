"""
End-to-End (E2E) / Acceptance Tests
Tests complete user workflows and scenarios
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


class TestUserWorkflows:
    """
    Acceptance tests based on user stories
    These test complete workflows that a user would perform
    """

    def test_complete_task_workflow(self, client: TestClient) -> None:
        """
        User Story: As a user, I want to create a task, update it,
        mark it complete, and then delete it.
        """
        # Step 1: Create a new task
        create_response = client.post("/tasks", json={
            "title": "Complete project documentation",
            "description": "Write comprehensive docs for the API",
            "priority": "high"
        })
        assert create_response.status_code == 201
        task = create_response.json()
        task_id = task["id"]
        assert task["completed"] is False

        # Step 2: Update the task description
        update_response = client.put(f"/tasks/{task_id}", json={
            "description": "Write comprehensive docs including examples"
        })
        assert update_response.status_code == 200
        assert "including examples" in update_response.json()["description"]

        # Step 3: Mark the task as complete
        complete_response = client.put(f"/tasks/{task_id}", json={
            "completed": True
        })
        assert complete_response.status_code == 200
        assert complete_response.json()["completed"] is True

        # Step 4: Verify it appears in completed filter
        filtered_response = client.get("/tasks?completed=true")
        assert filtered_response.status_code == 200
        completed_tasks = filtered_response.json()
        task_ids = [t["id"] for t in completed_tasks]
        assert task_id in task_ids

        # Step 5: Delete the task
        delete_response = client.delete(f"/tasks/{task_id}")
        assert delete_response.status_code == 204

        # Step 6: Verify it's deleted
        get_response = client.get(f"/tasks/{task_id}")
        assert get_response.status_code == 404

    def test_project_management_workflow(self, client: TestClient) -> None:
        """
        User Story: As a project manager, I want to create multiple tasks
        with different priorities and view statistics.
        """
        # Create multiple tasks
        tasks = [
            {"title": "Critical bug fix", "priority": "critical"},
            {"title": "Security update", "priority": "high"},
            {"title": "UI improvements", "priority": "medium"},
            {"title": "Documentation", "priority": "low"},
        ]

        created_ids = []
        for task_data in tasks:
            response = client.post("/tasks", json=task_data)
            assert response.status_code == 201
            created_ids.append(response.json()["id"])

        # Complete some tasks
        client.put(f"/tasks/{created_ids[0]}", json={"completed": True})
        client.put(f"/tasks/{created_ids[1]}", json={"completed": True})

        # Check statistics
        stats_response = client.get("/tasks/stats/summary")
        assert stats_response.status_code == 200
        stats = stats_response.json()

        # Verify stats are accurate (we have at least these 4 tasks)
        assert stats["total_tasks"] >= 4
        assert stats["completed_tasks"] >= 2
        assert stats["by_priority"]["critical"] >= 1

        # Cleanup
        for task_id in created_ids:
            client.delete(f"/tasks/{task_id}")

    def test_api_health_monitoring_workflow(self, client: TestClient) -> None:
        """
        User Story: As an ops engineer, I want to monitor API health
        and collect metrics.
        """
        # Check health endpoint
        health_response = client.get("/health")
        assert health_response.status_code == 200
        health = health_response.json()
        assert health["status"] == "healthy"
        assert health["database"] == "connected"

        # Make some requests to generate metrics
        client.get("/tasks")
        client.post("/tasks", json={"title": "Metrics test"})
        client.get("/tasks")

        # Check metrics endpoint
        metrics_response = client.get("/metrics")
        assert metrics_response.status_code == 200
        metrics = metrics_response.text

        # Verify expected metrics are present
        assert "http_requests_total" in metrics
        assert "http_request_duration_seconds" in metrics

    def test_api_error_handling(self, client: TestClient) -> None:
        """
        User Story: As a developer, I want clear error messages
        when something goes wrong.
        """
        # Test 404 error
        response = client.get("/tasks/999999")
        assert response.status_code == 404
        error = response.json()
        assert "detail" in error

        # Test validation error
        response = client.post("/tasks", json={
            "title": "",  # Empty title should fail
        })
        assert response.status_code == 422

        # Test invalid JSON
        response = client.post(
            "/tasks",
            content="not json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_concurrent_operations(self, client: TestClient) -> None:
        """
        User Story: As a user, I want the API to handle multiple
        operations without data corruption.
        """
        # Create multiple tasks rapidly
        task_ids = []
        for i in range(10):
            response = client.post(
                "/tasks",
                json={"title": f"Concurrent Task {i}"}
            )
            assert response.status_code == 201
            task_ids.append(response.json()["id"])

        # All IDs should be unique
        assert len(task_ids) == len(set(task_ids))

        # Update all tasks
        for task_id in task_ids:
            response = client.put(
                f"/tasks/{task_id}",
                json={"completed": True}
            )
            assert response.status_code == 200

        # Delete all tasks
        for task_id in task_ids:
            response = client.delete(f"/tasks/{task_id}")
            assert response.status_code == 204


class TestAPIContract:
    """
    Contract tests to ensure API responses match expected schema
    """

    def test_task_response_schema(self, client: TestClient) -> None:
        """Verify task response matches expected schema"""
        response = client.post("/tasks", json={"title": "Schema Test"})
        task = response.json()

        # Required fields
        assert "id" in task
        assert "title" in task
        assert "description" in task
        assert "priority" in task
        assert "completed" in task
        assert "created_at" in task
        assert "updated_at" in task

        # Type checks
        assert isinstance(task["id"], int)
        assert isinstance(task["title"], str)
        assert isinstance(task["completed"], bool)

        # Cleanup
        client.delete(f"/tasks/{task['id']}")

    def test_health_response_schema(self, client: TestClient) -> None:
        """Verify health response matches expected schema"""
        response = client.get("/health")
        health = response.json()

        assert "status" in health
        assert "timestamp" in health
        assert "version" in health
        assert "database" in health


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
