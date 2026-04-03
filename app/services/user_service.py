from sqlalchemy.orm import Session
from .. import models, schemas, auth


def create_user(user: schemas.UserCreate, db: Session) -> models.User:
    """
    Hashes the user's password and persists a new User record to the database.
    """
    hashed = auth.hash_password(user.password)
    db_user = models.User(
        username=user.username,
        password=hashed,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def list_users(db: Session) -> list[models.User]:
    """
    Returns all users in the system. Intended for admin use only
    (access control is enforced at the router level).
    """
    return db.query(models.User).all()