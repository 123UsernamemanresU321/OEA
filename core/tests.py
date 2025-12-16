from datetime import date, timedelta

import pytest
from django.urls import reverse

from .models import Attempt, Problem, ReviewItem


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(username="alice", password="pass1234")


@pytest.fixture
def other_user(django_user_model):
    return django_user_model.objects.create_user(username="bob", password="pass1234")


def test_scheduler_progression(user, db):
    item = ReviewItem.objects.create(user=user, prompt="p", answer_key="a")
    item.grade(ReviewItem.RATING_GOOD)
    first_due = item.due_date
    assert first_due >= date.today()
    first_interval = item.interval_days
    item.grade(ReviewItem.RATING_EASY)
    assert item.ease_factor >= 1.3
    assert item.interval_days >= first_interval
    assert item.due_date > first_due


def test_data_isolation_problem_detail(client, user, other_user):
    p1 = Problem.objects.create(
        title="A",
        source="Book",
        topic="NT",
        difficulty=5,
        tags="",
        statement="Test",
        created_by=user,
    )
    p2 = Problem.objects.create(
        title="B",
        source="Book",
        topic="ALG",
        difficulty=4,
        tags="",
        statement="Test",
        created_by=other_user,
    )
    client.login(username="alice", password="pass1234")
    resp_ok = client.get(reverse("problem_detail", args=[p1.pk]))
    assert resp_ok.status_code == 200
    resp_forbidden = client.get(reverse("problem_detail", args=[p2.pk]))
    assert resp_forbidden.status_code == 404


def test_dashboard_smoke(client, user):
    client.login(username="alice", password="pass1234")
    resp = client.get(reverse("dashboard"))
    assert resp.status_code == 200
    assert b"Dashboard" in resp.content
