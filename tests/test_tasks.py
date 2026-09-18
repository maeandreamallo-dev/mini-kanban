import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


@pytest.fixture(autouse=True)
def reset_database():
    """Create a clean database for every test."""
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    """Create a test client using the test database."""

    def override_get_db():
        db = TestingSessionLocal()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_task(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Restock ramen",
            "description": "Order Japanese frozen ramen",
            "priority": "high",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Restock ramen"
    assert data["description"] == "Order Japanese frozen ramen"
    assert data["priority"] == "high"
    assert data["status"] == "BACKLOG"
    assert "id" in data


def test_create_task_with_invalid_priority(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Test task",
            "priority": "invalid",
        },
    )

    assert response.status_code == 422


def test_create_task_with_empty_title(client):
    response = client.post(
        "/tasks",
        json={
            "title": "",
            "priority": "medium",
        },
    )

    assert response.status_code == 422


def test_get_task(client):
    create_response = client.post(
        "/tasks",
        json={
            "title": "Clean coffee machine",
            "priority": "medium",
        },
    )

    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == task_id
    assert data["title"] == "Clean coffee machine"


def test_get_nonexistent_task(client):
    response = client.get("/tasks/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_list_tasks(client):
    client.post(
        "/tasks",
        json={
            "title": "Task A",
            "priority": "low",
        },
    )

    client.post(
        "/tasks",
        json={
            "title": "Task B",
            "priority": "high",
        },
    )

    response = client.get("/tasks")

    assert response.status_code == 200

    tasks = response.json()

    assert len(tasks) == 2


def test_update_task(client):
    create_response = client.post(
        "/tasks",
        json={
            "title": "Original title",
            "priority": "low",
        },
    )

    task_id = create_response.json()["id"]

    response = client.put(
        f"/tasks/{task_id}",
        json={
            "title": "Updated title",
            "priority": "high",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Updated title"
    assert data["priority"] == "high"


def test_update_task_status(client):
    create_response = client.post(
        "/tasks",
        json={
            "title": "Prepare Green Apple Fizz",
            "priority": "high",
        },
    )

    task_id = create_response.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}/status",
        json={
            "status": "IN_PROGRESS",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "IN_PROGRESS"


def test_update_task_with_invalid_status(client):
    create_response = client.post(
        "/tasks",
        json={
            "title": "Test status",
            "priority": "medium",
        },
    )

    task_id = create_response.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}/status",
        json={
            "status": "INVALID_STATUS",
        },
    )

    assert response.status_code == 422


def test_delete_task(client):
    create_response = client.post(
        "/tasks",
        json={
            "title": "Temporary task",
            "priority": "low",
        },
    )

    task_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/tasks/{task_id}"
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/tasks/{task_id}"
    )

    assert get_response.status_code == 404


def test_delete_nonexistent_task(client):
    response = client.delete("/tasks/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_task_pagination(client):
    for number in range(3):
        client.post(
            "/tasks",
            json={
                "title": f"Pagination task {number}",
                "priority": "medium",
            },
        )

    response = client.get(
        "/tasks?skip=0&limit=2"
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_invalid_pagination_limit(client):
    response = client.get(
        "/tasks?limit=101"
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "limit must be between 1 and 100"
    )