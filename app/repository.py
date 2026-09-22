from datetime import date
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas


class ExpenseRepository:
    """Encapsulates all persistence access for Expense records.

    Isolating queries here keeps SQLAlchemy specifics out of route handlers
    and business logic, and gives the rest of the app a single seam to swap
    or mock for testing.
    """

    def __init__(self, db: Session):
        self._db = db

    def add(self, expense: schemas.ExpenseCreate) -> models.Expense:
        db_expense = models.Expense(
            amount=expense.amount,
            category=expense.category,
            note=expense.note,
            date=expense.date,
        )
        self._db.add(db_expense)
        self._db.commit()
        self._db.refresh(db_expense)
        return db_expense

    def get(self, expense_id: int) -> Optional[models.Expense]:
        return self._db.get(models.Expense, expense_id)

    def update(
        self, expense_id: int, expense: schemas.ExpenseUpdate
    ) -> Optional[models.Expense]:
        db_expense = self.get(expense_id)
        if db_expense is None:
            return None
        db_expense.amount = expense.amount
        db_expense.category = expense.category
        db_expense.note = expense.note
        db_expense.date = expense.date
        self._db.commit()
        self._db.refresh(db_expense)
        return db_expense

    def delete(self, expense_id: int) -> bool:
        db_expense = self.get(expense_id)
        if db_expense is None:
            return False
        self._db.delete(db_expense)
        self._db.commit()
        return True

    def _filtered_query(
        self,
        category: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ):
        query = self._db.query(models.Expense)
        if category:
            query = query.filter(models.Expense.category == category)
        if start_date:
            query = query.filter(models.Expense.date >= start_date)
        if end_date:
            query = query.filter(models.Expense.date <= end_date)
        return query

    def count(
        self,
        category: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> int:
        return self._filtered_query(category, start_date, end_date).count()

    def list(
        self,
        category: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[models.Expense]:
        query = self._filtered_query(category, start_date, end_date)
        return (
            query.order_by(models.Expense.date.desc(), models.Expense.id.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def distinct_categories(self) -> list[str]:
        rows = (
            self._db.query(models.Expense.category)
            .distinct()
            .order_by(models.Expense.category)
            .all()
        )
        return [row[0] for row in rows]

    def spend_by_category(self, start: date, end: date) -> dict[str, float]:
        rows = (
            self._db.query(models.Expense.category, func.sum(models.Expense.amount))
            .filter(models.Expense.date >= start, models.Expense.date <= end)
            .group_by(models.Expense.category)
            .all()
        )
        return {category: float(total) for category, total in rows}
