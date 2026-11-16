from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)

from app.models.user import User


def register_user(db: Session, full_name, email, password):

    existing = db.query(User).filter(User.email == email).first()

    if existing:
        return None

    user = User(
        full_name=full_name,
        email=email,
        password=hash_password(password),
    )

    db.add(user)

    db.commit()

    db.refresh(user)

    return user


def login_user(db: Session, email, password):

    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None

    if not verify_password(password, user.password):
        return None

    token = create_access_token(
        {
            "sub": user.email,
            "role": user.role,
        }
    )

    return token