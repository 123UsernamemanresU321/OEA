from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass
class ReviewState:
    ease_factor: float
    interval_days: int
    due_date: date


def grade_review(review_item, quality: int) -> ReviewState:
    """
    Apply a light SM-2 style update.

    quality: 0=Again, 1=Hard, 2=Good, 3=Easy
    """
    if quality not in (0, 1, 2, 3):
        raise ValueError("quality must be 0-3")

    ef = review_item.ease_factor or 2.5
    # SM-2 ease factor adjustment
    ef = ef + (0.1 - (3 - quality) * (0.08 + (3 - quality) * 0.02))
    ef = max(1.3, round(ef, 2))

    if quality < 2:
        interval = 1
    else:
        if review_item.interval_days <= 0:
            interval = 1 if quality == 2 else 3
        elif review_item.interval_days == 1:
            interval = 6
        else:
            interval = round(review_item.interval_days * ef)

    due = date.today() + timedelta(days=interval)

    review_item.ease_factor = ef
    review_item.interval_days = int(interval)
    review_item.due_date = due
    return ReviewState(ease_factor=ef, interval_days=interval, due_date=due)
