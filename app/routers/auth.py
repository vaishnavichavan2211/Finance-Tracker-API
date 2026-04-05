

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.schemas.user import TokenResponse, UserResponse
from app.services.user_service import fetch_user_by_email

router = APIRouter()


@router.post("/login", response_model=TokenResponse, summary="Login and get JWT token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):

    # Look up by email
    db_user = fetch_user_by_email(db, form_data.username)

    # Generic error message 
    auth_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not db_user or not verify_password(form_data.password, db_user.hashed_pw):
        raise auth_error

    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Contact an admin.",
        )

    # Create JWT with the user's email 
    token = create_access_token(data={"sub": db_user.email})

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.from_orm(db_user),
    )
