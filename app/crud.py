from sqlalchemy.orm import Session
from app.models import Task
from app.schemas import TaskCreate, TaskUpdate, TaskStatus

def get_task(db: Session, task_id: int) -> Task | None:
    """Retrieve a task by its ID."""

    return db.query(Task).filter(Task.id == task_id).first()

def get_tasks(db: Session, skip: int = 0, limit: int = 100,) -> list[Task]:
    """Retrieve a paginated list of tasks."""

    return (db.query(Task).offset(skip).limit(limit).all())

def create_task(db: Session, task: TaskCreate,) -> Task:
    """Create and persist a new task."""

    db_task = Task(
        title = task.title,
        description = task.description,
        priority = task.priority.value,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task

def update_task(db: Session, db_task: Task, task: TaskUpdate) -> Task:
    """Update an existing task."""

    update_data = task.model_dump(exclude_unset = True)
    if "priority" in update_data:
        update_data["priority"] = update_data["priority"].value
    
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db.commit()
    db.refresh(db_task)

    return db_task

def update_task_status(db: Session, db_task: Task, status: TaskStatus,) -> Task:
    """Move a task to a different Kanban status."""

    db_task.status = status.value
    db.commit()
    db.refresh(db_task)

    return db_task

def delete_task(db: Session, db_task: Task,) -> None:
    """Delete a task from the database."""

    db.delete(db_task)
    db.commit()