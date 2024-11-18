from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from backend.db_depends import get_db
from typing import Annotated
from models import User
from schemas import CreateUser, UpdateUser
from sqlalchemy import select, insert, update, delete
from slugify import slugify

router = APIRouter()


# Функция для получения всех пользователей
@router.get("/", response_model=list[User])
def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.exec(select(User)).scalars().all()
    return users


# Функция для получения пользователя по ID
@router.get("/{user_id}", response_model=User)
def user_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.exec(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")
    return user


# Функция для создания нового пользователя
@router.post("/create", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: CreateUser, db: Annotated[Session, Depends(get_db)]):
    new_user = User(**user.dict())
    new_user.slug = slugify(user.username)  # Создаём slug на основе имени пользователя
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.put("/{user_id}", response_model=User)
def update_user(user_id: int, user_update: UpdateUser, db: Annotated[Session, Depends(get_db)]):
    user = db.exec(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")

    # Обновление пользователя
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.exec(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")

    db.delete(user)
    db.commit()
    return
