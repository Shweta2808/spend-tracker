"""Pluggable spend insights.

Each Insight inspects the current vs. previous period's per-category spend
and returns any findings worth surfacing in the summary. New insights (e.g.
a budget-threshold alert, a trailing-average comparison) can be added by
implementing this interface and registering an instance with SummaryService,
without touching the aggregation logic in summary_service.py.
"""

from abc import ABC, abstractmethod

from app import schemas


class Insight(ABC):
    @abstractmethod
    def evaluate(
        self,
        current_by_category: dict[str, float],
        previous_by_category: dict[str, float],
    ) -> list[schemas.CategorySpike]:
        """Return findings derived from comparing two periods' category spend."""
        raise NotImplementedError


class CategorySpikeInsight(Insight):
    """Flags categories whose spend rose more than `threshold_percent` month over month.

    Categories with no prior-period spend are skipped rather than reported as
    an infinite/undefined increase.
    """

    def __init__(self, threshold_percent: float = 20.0):
        self.threshold_percent = threshold_percent

    def evaluate(
        self,
        current_by_category: dict[str, float],
        previous_by_category: dict[str, float],
    ) -> list[schemas.CategorySpike]:
        spikes: list[schemas.CategorySpike] = []
        for category, current_total in current_by_category.items():
            previous_total = previous_by_category.get(category)
            if not previous_total or previous_total <= 0:
                continue
            percent_change = ((current_total - previous_total) / previous_total) * 100
            if percent_change > self.threshold_percent:
                spikes.append(
                    schemas.CategorySpike(
                        category=category,
                        current_total=current_total,
                        previous_total=previous_total,
                        percent_change=percent_change,
                    )
                )
        return spikes
