

from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.models.user import User
from app.schemas.user import (
    PasswordChangeRequest,
    UserCreateRequest,
    UserResponse,
    UserUpdateRequest,
)
from app.services import user_service

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user (public)",
)
def register(payload: UserCreateRequest, db: Session = Depends(get_db)):
  
    return user_service.register_new_user(db, payload)


@router.get("/me", response_model=UserResponse, summary="Get your own profile")
def get_my_profile(current_user: User = Depends(get_current_user)):
   
    return current_user


@router.post("/me/change-password", summary="Change your password")
def change_my_password(
    payload: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return user_service.change_user_password(
        db, current_user, payload.current_password, payload.new_password
    )


@router.get(
    "/",
    response_model=List[UserResponse],
    summary="List all users (Admin only)",
)
def list_all_users(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),   
):

    return user_service.fetch_all_users(db, skip=skip, limit=limit)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get a user by ID (Admin only)",
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return user_service.fetch_user_by_id(db, user_id)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update a user (Admin only)",
)
def update_user(
    user_id: int,
    payload: UserUpdateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
 
    return user_service.modify_user(db, user_id, payload)


@router.delete(
    "/{user_id}",
    summary="Delete a user and all their records (Admin only)",
    status_code=status.HTTP_200_OK,
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return user_service.remove_user(db, user_id)
