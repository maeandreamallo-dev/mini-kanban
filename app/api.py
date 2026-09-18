from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import(
    TaskCreate,
    TaskResponse,
    TaskStatusUpdate,
    TaskUpdate,
)

router = APIRouter(prefix = "/tasks", tags = ["Tasks"],)

@router.post("", response_model = TaskResponse, status_code = status.HTTP_201_CREATED,)
def create_task(task: TaskCreate, db: Session = Depends(get_db),):
    """Create a new Kanban task."""

    return crud.create_task(db, task)

@router.get("", response_model = list[TaskResponse],)
def list_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),):
    """Return a paginated list of tasks."""

    if skip < 0: 
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "skip must be greater than or equal to 0",)
    if limit < 1 or limit > 100: 
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "limit must be between 1 and 100",)

    return crud.get_tasks(db, skip = skip, limit = limit,)

@router.get("/{task_id}", response_model = TaskResponse,)
def get_task(task_id: int, db: Session = Depends(get_db),):
    """Return a task by ID."""

    task = crud.get_task(db, task_id)

    if task is None: 
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Task not found", )

    return task

@router.put("/{task_id}", response_model = TaskResponse,)
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db), ):
    """Update an existing task."""

    db_task = crud.get_task(db, task_id)

    if db_task is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Task not found.",)

    return crud.update_task(db, db_task, task,)

@router.patch("/{task_id}/status", response_model = TaskResponse, )
def update_task_status(task_id: int, task_status: TaskStatusUpdate, db: Session = Depends(get_db),):
    """Move a task to another Kanban status."""

    db_task = crud.get_task(db, task_id)

    if db_task is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Task not found",)

    return crud.update_task_status(db, db_task, task_status.status,)

@router.delete("/{task_id}", status_code = status.HTTP_204_NO_CONTENT, )
def delete_task(task_id: int, db: Session = Depends(get_db),):
    """Delete task."""

    db_task = crud.get_task(db, task_id)

    if db_task is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Task not found", )

    crud.delete_task(db, db_task)