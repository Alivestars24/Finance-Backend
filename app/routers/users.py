from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import schemas, database
from ..dependencies import require_roles
from ..services import user_service

router = APIRouter(prefix="/users")


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    return user_service.create_user(user=user, db=db)


@router.get("/")
def list_users(
    db: Session = Depends(get_db),
    user=Depends(require_roles(["admin"]))
):
    return user_service.list_users(db=db)