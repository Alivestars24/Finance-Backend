from sqlalchemy.orm import Session
from fastapi import HTTPException
from .. import models, auth


def login_user(username: str, password: str, db: Session) -> dict:
    """
    Validates user credentials and returns a JWT access token.
    Raises 400 if credentials are invalid.
    """
    user = db.query(models.User).filter_by(username=username).first()

    if not user or not auth.verify_password(password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = auth.create_token({
        "username": user.username,
        "role": user.role,
        "user_id": user.id
    })

    return {"access_token": token}