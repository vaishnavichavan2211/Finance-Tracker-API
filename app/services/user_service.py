
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User, UserRole
from app.schemas.user import UserCreateRequest, UserUpdateRequest


def fetch_all_users(db: Session, skip: int = 0, limit: int = 20) -> List[User]:
    """Return a paginated list of all users (Admin only)."""
    return db.query(User).offset(skip).limit(limit).all()


def fetch_user_by_id(db: Session, user_id: int) -> User:
    """Look up a single user — raise 404 if not found."""
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} was not found.",
        )
    return db_user


def fetch_user_by_email(db: Session, email: str) -> Optional[User]:
    """Return a user by email, or None if not found."""
    return db.query(User).filter(User.email == email).first()


def register_new_user(db: Session, payload: UserCreateRequest) -> User:
    """
    Create a new user account.
    Raises 409 if the email is already registered.
    """
    if fetch_user_by_email(db, payload.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    new_user = User(
        full_name = payload.full_name,
        email     = payload.email,
        hashed_pw = hash_password(payload.password),  # Never store plain-text!
        role      = payload.role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)   # Load the auto-generated user_id and created_at
    return new_user


def modify_user(db: Session, user_id: int, payload: UserUpdateRequest) -> User:
    """Update selected fields on an existing user."""
    db_user = fetch_user_by_id(db, user_id)

    # Only update fields that were actually sent
    update_data = payload.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def remove_user(db: Session, user_id: int) -> dict:
    """Hard-delete a user and their records (cascade handles the records)."""
    db_user = fetch_user_by_id(db, user_id)
    db.delete(db_user)
    db.commit()
    return {"message": f"User {user_id} deleted successfully."}


def change_user_password(
    db: Session,
    db_user: User,
    current_password: str,
    new_password: str,
) -> dict:
    """
    Let a user update their own password.
    Verifies the current password before accepting the new one.
    """
    if not verify_password(current_password, db_user.hashed_pw):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect.",
        )
    db_user.hashed_pw = hash_password(new_password)
    db.commit()
    return {"message": "Password updated successfully."}
