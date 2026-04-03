from sqlalchemy.orm import Session
from .. import models, schemas


def create_record(
    record: schemas.RecordCreate,
    current_user: dict,
    db: Session
) -> models.Record:
    """
    Creates a new financial record. If no owner_id is provided in the
    payload, the record is assigned to the currently authenticated user.
    """
    db_record = models.Record(
        amount=record.amount,
        type=record.type,
        category=record.category,
        date=record.date,
        notes=record.notes,
        owner_id=record.owner_id or current_user["user_id"]
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def get_records(
    current_user: dict,
    db: Session,
    skip: int = 0,
    limit: int = 10,
    category: str | None = None,
    type: str | None = None
) -> list[models.Record]:
    """
    Returns a filtered, paginated list of financial records belonging
    to the currently authenticated user.

    Filters:
        - category: exact match on the record category field
        - type: either "income" or "expense"
        - skip / limit: standard pagination offsets
    """
    query = db.query(models.Record).filter(
        models.Record.owner_id == current_user["user_id"]
    )

    if category:
        query = query.filter(models.Record.category == category)
    if type:
        query = query.filter(models.Record.type == type)

    return query.offset(skip).limit(limit).all()