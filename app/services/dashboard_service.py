from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models


def get_summary(current_user: dict, db: Session) -> dict:
    """
    Computes and returns top-level financial summary for the current user:
        - total_income:   sum of all income records
        - total_expense:  sum of all expense records
        - net_balance:    income minus expenses
    """
    income = db.query(func.sum(models.Record.amount)).filter(
        models.Record.type == "income",
        models.Record.owner_id == current_user["user_id"]
    ).scalar() or 0

    expense = db.query(func.sum(models.Record.amount)).filter(
        models.Record.type == "expense",
        models.Record.owner_id == current_user["user_id"]
    ).scalar() or 0

    return {
        "total_income": income,
        "total_expense": expense,
        "net_balance": income - expense
    }


def get_category_breakdown(current_user: dict, db: Session) -> list[dict]:
    """
    Groups the current user's records by category and sums the amounts,
    returning a list of { category, total } objects for dashboard display.
    """
    results = db.query(
        models.Record.category,
        func.sum(models.Record.amount)
    ).filter(
        models.Record.owner_id == current_user["user_id"]
    ).group_by(models.Record.category).all()

    return [
        {"category": r[0], "total": r[1]}
        for r in results
    ]