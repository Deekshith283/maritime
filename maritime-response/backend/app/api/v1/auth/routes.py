from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
)
from app.services.auth_services import (
    login_user,
    register_user,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.post("/register")
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):

    user = register_user(
        db,
        request.full_name,
        request.email,
        request.password,
    )

    if user is None:
        raise HTTPException(
            status_code=400,
            detail="Email already exists",
        )

    return {
        "message": "User registered successfully"
    }


@router.post("/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):

    token = login_user(
        db,
        request.email,
        request.password,
    )

    if token is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    return {
        "access_token": token,
        "token_type": "bearer",
    }