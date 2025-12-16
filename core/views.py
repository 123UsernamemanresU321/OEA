from __future__ import annotations

import json
from datetime import date, datetime, timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Count
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .filters import ProblemFilter
from .forms import (
    AttemptForm,
    ImportForm,
    MistakeForm,
    ProblemForm,
    RegisterForm,
    ReviewGradeForm,
)
from .models import Attempt, Mistake, MistakeType, Problem, ReviewItem, TOPIC_CHOICES


def landing(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "landing.html")


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Welcome to Olympiad Error Atlas!")
        return redirect("dashboard")
    return render(request, "registration/register.html", {"form": form})


@login_required
def dashboard(request):
    today = date.today()
    last_30 = timezone.now() - timedelta(days=30)
    last_7 = timezone.now() - timedelta(days=7)
    attempts = Attempt.objects.filter(user=request.user, started_at__gte=last_30)
    due_reviews = ReviewItem.objects.filter(user=request.user, due_date__lte=today)

    top_mistakes = (
        Mistake.objects.filter(attempt__user=request.user)
        .values("mistake_type__name")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )

    topic_counts = (
        Attempt.objects.filter(user=request.user)
        .values("problem__topic")
        .annotate(total=Count("id"))
        .order_by()
    )

    context = {
        "due_reviews": due_reviews,
        "attempts_last7": attempts.filter(started_at__gte=last_7).count(),
        "attempts_last30": attempts.count(),
        "top_mistakes": top_mistakes,
        "topic_labels": [dict(TOPIC_CHOICES).get(i["problem__topic"], i["problem__topic"]) for i in topic_counts],
        "topic_data": [i["total"] for i in topic_counts],
        "recent_attempts": attempts.select_related("problem")[:5],
    }
    return render(request, "dashboard.html", context)


@login_required
def problem_list(request):
    qs = Problem.objects.filter(created_by=request.user)
    problem_filter = ProblemFilter(request.GET, queryset=qs)
    return render(
        request,
        "problems/list.html",
        {
            "filter": problem_filter,
            "problems": problem_filter.qs,
            "selected_topics": request.GET.getlist("topic"),
        },
    )


@login_required
def problem_create(request):
    form = ProblemForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        problem = form.save(commit=False)
        problem.created_by = request.user
        problem.save()
        messages.success(request, "Problem created.")
        return redirect("problem_detail", pk=problem.pk)
    return render(request, "problems/form.html", {"form": form, "title": "Create Problem"})


@login_required
def problem_detail(request, pk):
    problem = get_object_or_404(Problem, pk=pk, created_by=request.user)
    attempts = problem.attempts.filter(user=request.user)
    return render(request, "problems/detail.html", {"problem": problem, "attempts": attempts})


@login_required
def problem_edit(request, pk):
    problem = get_object_or_404(Problem, pk=pk, created_by=request.user)
    form = ProblemForm(request.POST or None, instance=problem)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Problem updated.")
        return redirect("problem_detail", pk=pk)
    return render(request, "problems/form.html", {"form": form, "title": "Edit Problem"})


@login_required
def attempt_list(request):
    attempts = Attempt.objects.filter(user=request.user).select_related("problem")
    return render(request, "attempts/list.html", {"attempts": attempts})


@login_required
def start_attempt(request, problem_id):
    problem = get_object_or_404(Problem, pk=problem_id, created_by=request.user)
    attempt = Attempt.objects.create(problem=problem, user=request.user, started_at=timezone.now())
    messages.info(request, "Attempt started. Finish when you are done.")
    return redirect("finish_attempt", pk=attempt.pk)


@login_required
def finish_attempt(request, pk):
    attempt = get_object_or_404(Attempt, pk=pk, user=request.user)
    form = AttemptForm(request.POST or None, instance=attempt)
    if request.method == "POST" and form.is_valid():
        attempt = form.save(commit=False)
        attempt.ended_at = timezone.now()
        attempt.save()
        messages.success(request, "Attempt saved.")
        return redirect("attempt_list")
    return render(request, "attempts/finish.html", {"form": form, "attempt": attempt})


@login_required
def add_mistake(request, attempt_id):
    attempt = get_object_or_404(Attempt, pk=attempt_id, user=request.user)
    form = MistakeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        mistake = form.save(commit=False)
        mistake.attempt = attempt
        mistake.save()
        ReviewItem.objects.create(
            user=request.user,
            related_mistake=mistake,
            prompt=mistake.short_label,
            answer_key=mistake.detailed_postmortem,
            due_date=mistake.next_review_date or date.today(),
        )
        messages.success(request, "Mistake recorded and review scheduled.")
        return redirect("finish_attempt", pk=attempt_id)
    return render(request, "mistakes/form.html", {"form": form, "attempt": attempt})


@login_required
def mistake_analytics(request):
    mistakes = Mistake.objects.filter(attempt__user=request.user).select_related("mistake_type", "attempt")
    heatmap = {}
    for m in mistakes:
        topic = dict(TOPIC_CHOICES).get(m.attempt.problem.topic, m.attempt.problem.topic)
        mtype = m.mistake_type.name
        heatmap.setdefault(topic, {}).setdefault(mtype, 0)
        heatmap[topic][mtype] += 1

    trend = (
        mistakes.annotate(month=models.functions.TruncMonth("attempt__started_at"))
        .values("month")
        .annotate(total=Count("id"))
        .order_by("month")
    )

    repeat_risk = (
        mistakes.values("mistake_type__name")
        .annotate(total=Count("id"))
        .filter(total__gte=2)
        .order_by("-total")
    )
    type_headers = sorted({t for types in heatmap.values() for t in types.keys()})
    return render(
        request,
        "mistakes/analytics.html",
        {"heatmap": heatmap, "trend": list(trend), "repeat_risk": repeat_risk, "type_headers": type_headers},
    )


@login_required
def review_queue(request):
    due_items = ReviewItem.objects.filter(user=request.user, due_date__lte=date.today()).order_by("due_date")
    current = due_items.first()
    grade_form = ReviewGradeForm()
    return render(
        request,
        "reviews/queue.html",
        {"current": current, "grade_form": grade_form, "queue_size": due_items.count()},
    )


@login_required
@require_POST
def grade_review(request, pk):
    item = get_object_or_404(ReviewItem, pk=pk, user=request.user)
    form = ReviewGradeForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest("Invalid rating")
    rating = int(form.cleaned_data["rating"])
    item.grade(rating)
    messages.success(request, "Review graded.")
    return redirect("review_queue")


@login_required
def export_data(request):
    problems = list(Problem.objects.filter(created_by=request.user))
    attempts = list(Attempt.objects.filter(user=request.user))
    mistakes = list(Mistake.objects.filter(attempt__user=request.user))
    reviews = list(ReviewItem.objects.filter(user=request.user))
    mistake_types = list(MistakeType.objects.all())

    data = {
        "problems": [
            {
                "id": p.id,
                "title": p.title,
                "source": p.source,
                "topic": p.topic,
                "difficulty": p.difficulty,
                "tags": p.tags,
                "statement": p.statement,
                "created_at": p.created_at.isoformat(),
            }
            for p in problems
        ],
        "attempts": [
            {
                "id": a.id,
                "problem": a.problem.id,
                "started_at": a.started_at.isoformat() if a.started_at else None,
                "ended_at": a.ended_at.isoformat() if a.ended_at else None,
                "outcome": a.outcome,
                "final_answer": a.final_answer,
                "solution_notes": a.solution_notes,
                "confidence": a.confidence,
            }
            for a in attempts
        ],
        "mistake_types": [
            {"name": mt.name, "description": mt.description} for mt in mistake_types
        ],
        "mistakes": [
            {
                "attempt": m.attempt.id,
                "mistake_type": m.mistake_type.name,
                "severity": m.severity,
                "short_label": m.short_label,
                "detailed_postmortem": m.detailed_postmortem,
                "conceptual_gap": m.conceptual_gap,
                "execution_error": m.execution_error,
                "strategy_error": m.strategy_error,
                "fix_plan": m.fix_plan,
                "next_review_date": m.next_review_date.isoformat() if m.next_review_date else None,
            }
            for m in mistakes
        ],
        "reviews": [
            {
                "related_mistake": r.related_mistake.short_label if r.related_mistake else None,
                "related_problem": r.related_problem.title if r.related_problem else None,
                "prompt": r.prompt,
                "answer_key": r.answer_key,
                "ease_factor": r.ease_factor,
                "interval_days": r.interval_days,
                "due_date": r.due_date.isoformat(),
            }
            for r in reviews
        ],
    }
    response = HttpResponse(json.dumps(data, indent=2), content_type="application/json")
    response["Content-Disposition"] = 'attachment; filename="olympiad_error_atlas.json"'
    return response


def _parse_datetime(value: str | None):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _parse_date(value: str | None):
    dt = _parse_datetime(value)
    if dt:
        return dt.date()
    return None


@login_required
def import_data(request):
    form = ImportForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        uploaded = form.cleaned_data["file"]
        try:
            payload = json.load(uploaded)
        except json.JSONDecodeError:
            messages.error(request, "Invalid JSON file.")
            return render(request, "import_export/import.html", {"form": form})
        mistake_type_map = {}
        for mt in payload.get("mistake_types", []):
            obj, _ = MistakeType.objects.get_or_create(
                name=mt.get("name"), defaults={"description": mt.get("description", "")}
            )
            mistake_type_map[obj.name] = obj

        problem_map = {}
        for p in payload.get("problems", []):
            obj = Problem.objects.create(
                title=p.get("title", "Untitled"),
                source=p.get("source", ""),
                topic=p.get("topic", "OTHER"),
                difficulty=p.get("difficulty", 5),
                tags=p.get("tags", ""),
                statement=p.get("statement", ""),
                created_by=request.user,
            )
            problem_map[p.get("id")] = obj

        attempt_map = {}
        for a in payload.get("attempts", []):
            problem = problem_map.get(a.get("problem"))
            if not problem:
                continue
            att = Attempt.objects.create(
                problem=problem,
                user=request.user,
                started_at=_parse_datetime(a.get("started_at")) or timezone.now(),
                ended_at=_parse_datetime(a.get("ended_at")),
                outcome=a.get("outcome", "stuck"),
                final_answer=a.get("final_answer", ""),
                solution_notes=a.get("solution_notes", ""),
                confidence=a.get("confidence", 3),
            )
            attempt_map[a.get("id")] = att
        for m in payload.get("mistakes", []):
            attempt = attempt_map.get(m.get("attempt"))
            mtype = mistake_type_map.get(m.get("mistake_type"))
            if not attempt or not mtype:
                continue
            Mistake.objects.create(
                attempt=attempt,
                mistake_type=mtype,
                severity=m.get("severity", 3),
                short_label=m.get("short_label", "Mistake"),
                detailed_postmortem=m.get("detailed_postmortem", ""),
                conceptual_gap=m.get("conceptual_gap", False),
                execution_error=m.get("execution_error", False),
                strategy_error=m.get("strategy_error", False),
                fix_plan=m.get("fix_plan", ""),
                next_review_date=_parse_date(m.get("next_review_date")),
            )
        for r in payload.get("reviews", []):
            related_mistake = None
            related_problem = None
            if r.get("related_mistake"):
                related_mistake = Mistake.objects.filter(
                    short_label=r.get("related_mistake"), attempt__user=request.user
                ).first()
            if r.get("related_problem"):
                related_problem = Problem.objects.filter(
                    title=r.get("related_problem"), created_by=request.user
                ).first()
            ReviewItem.objects.create(
                user=request.user,
                related_mistake=related_mistake,
                related_problem=related_problem,
                prompt=r.get("prompt", ""),
                answer_key=r.get("answer_key", ""),
                ease_factor=r.get("ease_factor", 2.5),
                interval_days=r.get("interval_days", 0),
                due_date=_parse_date(r.get("due_date")) or date.today(),
            )
        messages.success(request, "Data imported.")
        return redirect("dashboard")
    return render(request, "import_export/import.html", {"form": form})
