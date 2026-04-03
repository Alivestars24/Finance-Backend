from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import database
from fastapi.security import OAuth2PasswordRequestForm
from ..services import auth_service

router = APIRouter(prefix="/auth")


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    return auth_service.login_user(
        username=form_data.username,
        password=form_data.password,
        db=db
    )