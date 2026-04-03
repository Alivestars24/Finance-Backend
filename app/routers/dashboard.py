from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import database
from ..dependencies import require_roles
from ..services import dashboard_service

router = APIRouter(prefix="/dashboard")


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/summary")
def summary(
    db: Session = Depends(get_db),
    user=Depends(require_roles(["admin", "analyst"]))
):
    return dashboard_service.get_summary(current_user=user, db=db)


@router.get("/category")
def category_breakdown(
    db: Session = Depends(get_db),
    user=Depends(require_roles(["admin", "analyst"]))
):
    return dashboard_service.get_category_breakdown(current_user=user, db=db)