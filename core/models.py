from __future__ import annotations

from datetime import date, datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone

from .scheduler import grade_review

User = get_user_model()


TOPIC_CHOICES = [
    ("NT", "Number Theory"),
    ("ALG", "Algebra"),
    ("GEO", "Geometry"),
    ("COMB", "Combinatorics"),
    ("OTHER", "Other"),
]


class Problem(models.Model):
    title = models.CharField(max_length=200)
    source = models.CharField(max_length=200, blank=True)
    topic = models.CharField(max_length=10, choices=TOPIC_CHOICES)
    difficulty = models.PositiveSmallIntegerField(
        default=5, validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    tags = models.CharField(max_length=200, blank=True)
    statement = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    @property
    def tag_list(self) -> list[str]:
        return [t.strip() for t in self.tags.split(",") if t.strip()]


class Attempt(models.Model):
    OUTCOME_CHOICES = [
        ("solved", "Solved"),
        ("partial", "Partial"),
        ("stuck", "Stuck"),
        ("wrong", "Wrong"),
    ]

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="attempts")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)
    time_spent_seconds = models.PositiveIntegerField(default=0)
    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES, default="stuck")
    final_answer = models.TextField(blank=True)
    solution_notes = models.TextField(blank=True)
    confidence = models.PositiveSmallIntegerField(
        default=3, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    class Meta:
        ordering = ["-started_at"]

    def __str__(self) -> str:
        return f"{self.problem.title} ({self.get_outcome_display()})"

    def save(self, *args, **kwargs):
        if self.started_at and self.ended_at:
            start = self.started_at
            end = self.ended_at
            if isinstance(start, datetime) and isinstance(end, datetime):
                delta = end - start
                self.time_spent_seconds = max(0, int(delta.total_seconds()))
        super().save(*args, **kwargs)

    @property
    def duration_display(self) -> str:
        minutes, seconds = divmod(self.time_spent_seconds, 60)
        return f"{minutes}m {seconds}s"


class MistakeType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Mistake(models.Model):
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name="mistakes")
    mistake_type = models.ForeignKey(MistakeType, on_delete=models.CASCADE)
    severity = models.PositiveSmallIntegerField(
        default=3, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    short_label = models.CharField(max_length=150)
    detailed_postmortem = models.TextField()
    conceptual_gap = models.BooleanField(default=False)
    execution_error = models.BooleanField(default=False)
    strategy_error = models.BooleanField(default=False)
    fix_plan = models.TextField(blank=True)
    next_review_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-severity"]

    def __str__(self) -> str:
        return self.short_label


class ReviewItem(models.Model):
    RATING_AGAIN = 0
    RATING_HARD = 1
    RATING_GOOD = 2
    RATING_EASY = 3

    RATING_CHOICES = [
        (RATING_AGAIN, "Again"),
        (RATING_HARD, "Hard"),
        (RATING_GOOD, "Good"),
        (RATING_EASY, "Easy"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    related_mistake = models.ForeignKey(
        Mistake, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviews"
    )
    related_problem = models.ForeignKey(
        Problem, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviews"
    )
    prompt = models.TextField()
    answer_key = models.TextField()
    ease_factor = models.FloatField(default=2.5)
    interval_days = models.PositiveIntegerField(default=0)
    due_date = models.DateField(default=date.today)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["due_date"]

    def __str__(self) -> str:
        return f"Review for {self.related_mistake or self.related_problem}"

    def is_due(self) -> bool:
        return self.due_date <= date.today()

    def grade(self, rating: int) -> None:
        grade_review(self, rating)
        self.save()
