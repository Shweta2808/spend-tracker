import calendar
from datetime import date
from typing import Optional

from app import schemas
from app.insights import CategorySpikeInsight, Insight
from app.repository import ExpenseRepository


def _month_bounds(month: str) -> tuple[date, date]:
    year, mon = (int(part) for part in month.split("-"))
    start = date(year, mon, 1)
    end = date(year, mon, calendar.monthrange(year, mon)[1])
    return start, end


def _previous_month(month: str) -> str:
    year, mon = (int(part) for part in month.split("-"))
    if mon == 1:
        return f"{year - 1}-12"
    return f"{year}-{mon - 1:02d}"


class SummaryService:
    """Builds the /summary response from repository data plus registered insights.

    Insights are injected rather than hardcoded, so additional checks can be
    composed in (or swapped out, e.g. per-environment) without changing this
    class.
    """

    def __init__(
        self,
        repository: ExpenseRepository,
        insights: Optional[list[Insight]] = None,
    ):
        self._repository = repository
        self._insights = insights if insights is not None else [CategorySpikeInsight()]

    def build(self, month: str) -> schemas.SummaryOut:
        start, end = _month_bounds(month)
        current_by_category = self._repository.spend_by_category(start, end)
        total_spend = sum(current_by_category.values())

        prev_start, prev_end = _month_bounds(_previous_month(month))
        previous_by_category = self._repository.spend_by_category(prev_start, prev_end)
        previous_total = sum(previous_by_category.values())

        absolute_change = total_spend - previous_total
        percent_change = (
            (absolute_change / previous_total) * 100 if previous_total > 0 else None
        )

        spikes: list[schemas.CategorySpike] = []
        for insight in self._insights:
            spikes.extend(insight.evaluate(current_by_category, previous_by_category))

        return schemas.SummaryOut(
            month=month,
            total_spend=total_spend,
            spend_by_category=current_by_category,
            month_over_month_change=schemas.MonthOverMonthChange(
                current_total=total_spend,
                previous_total=previous_total,
                absolute_change=absolute_change,
                percent_change=percent_change,
            ),
            category_spikes=spikes,
        )
