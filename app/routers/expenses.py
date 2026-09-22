from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app import schemas
from app.auth import require_api_key
from app.dependencies import get_expense_repository
from app.repository import ExpenseRepository
from app.utils import normalize_category

router = APIRouter(prefix="/expenses", tags=["expenses"], dependencies=[Depends(require_api_key)])


@router.post("", response_model=schemas.ExpenseOut, status_code=201)
def create_expense(
    expense: schemas.ExpenseCreate,
    repository: ExpenseRepository = Depends(get_expense_repository),
):
    return repository.add(expense)


@router.get("", response_model=schemas.ExpenseListOut)
def list_expenses(
    category: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    repository: ExpenseRepository = Depends(get_expense_repository),
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=400, detail="start_date must not be after end_date"
        )
    normalized_category = normalize_category(category) if category else None
    items = repository.list(
        category=normalized_category,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )
    total = repository.count(
        category=normalized_category, start_date=start_date, end_date=end_date
    )
    return schemas.ExpenseListOut(items=items, total=total, limit=limit, offset=offset)


@router.get("/categories", response_model=list[str])
def list_expense_categories(
    repository: ExpenseRepository = Depends(get_expense_repository),
):
    return repository.distinct_categories()


@router.put("/{expense_id}", response_model=schemas.ExpenseOut)
def update_expense(
    expense_id: int,
    expense: schemas.ExpenseUpdate,
    repository: ExpenseRepository = Depends(get_expense_repository),
):
    updated = repository.update(expense_id, expense)
    if updated is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return updated


@router.delete("/{expense_id}", status_code=204, response_model=None)
def delete_expense(
    expense_id: int,
    repository: ExpenseRepository = Depends(get_expense_repository),
):
    deleted = repository.delete(expense_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Expense not found")
    return None
