from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.db_depends import get_db
from models import Task, User
from schemas import CreateTask
from sqlalchemy import select

router = APIRouter()


@router.get("/", response_model=list[Task])
async def all_tasks(db: Session = Depends(get_db)):
    tasks = db.execute(select(Task)).scalars().all()
    return tasks


@router.get("/task/{task_id}", response_model=Task)
async def task_by_id(task_id: int, db: Session = Depends(get_db)):
    task = db.execute(select(Task).filter(Task.id == task_id)).scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=Task)
async def create_task(task: CreateTask, db: Session = Depends(get_db)):
    user = db.execute(select(User).filter(User.id == task.user_id)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User was not found")
    new_task = Task(**task.dict())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@router.put("/update/{task_id}", response_model=Task)
async def update_task(task_id: int, task: CreateTask, db: Session = Depends(get_db)):
    db_task = db.execute(select(Task).filter(Task.id == task_id)).scalar_one_or_none()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in task.dict().items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.delete("/delete/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.execute(select(Task).filter(Task.id == task_id)).scalar_one_or_none()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}
