from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import schemas, database
from ..dependencies import require_roles
from ..services import record_service

router = APIRouter(prefix="/records")


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.RecordOut)
def create_record(
    record: schemas.RecordCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles(["admin"]))
):
    return record_service.create_record(record=record, current_user=user, db=db)


@router.get("/")
def get_records(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
    category: str | None = None,
    type: str | None = None,
    user=Depends(require_roles(["admin", "analyst", "viewer"]))
):
    return record_service.get_records(
        current_user=user,
        db=db,
        skip=skip,
        limit=limit,
        category=category,
        type=type
    )