from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repository import ExpenseRepository
from app.summary_service import SummaryService


def get_expense_repository(db: Session = Depends(get_db)) -> ExpenseRepository:
    return ExpenseRepository(db)


def get_summary_service(
    repository: ExpenseRepository = Depends(get_expense_repository),
) -> SummaryService:
    return SummaryService(repository)
