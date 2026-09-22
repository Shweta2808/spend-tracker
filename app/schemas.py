from datetime import date as date_type
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, field_validator

from app.utils import normalize_category


class ExpenseCreate(BaseModel):
    amount: float = Field(gt=0, description="Must be a positive amount")
    category: str = Field(min_length=1)
    note: Optional[str] = None
    date: date_type

    @field_validator("category")
    @classmethod
    def _normalize_category(cls, value: str) -> str:
        normalized = normalize_category(value)
        if not normalized:
            raise ValueError("category must not be empty")
        return normalized


class ExpenseUpdate(ExpenseCreate):
    pass


class ExpenseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: float
    category: str
    note: Optional[str]
    date: date_type


class ExpenseListOut(BaseModel):
    items: list[ExpenseOut]
    total: int
    limit: int
    offset: int


class MonthOverMonthChange(BaseModel):
    current_total: float
    previous_total: float
    absolute_change: float
    percent_change: Optional[float]


class CategorySpike(BaseModel):
    category: str
    current_total: float
    previous_total: float
    percent_change: float


class SummaryOut(BaseModel):
    month: str
    total_spend: float
    spend_by_category: dict[str, float]
    month_over_month_change: MonthOverMonthChange
    category_spikes: list[CategorySpike]
