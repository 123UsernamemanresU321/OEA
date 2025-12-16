from django.contrib import admin

from .models import Attempt, Mistake, MistakeType, Problem, ReviewItem


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ("title", "topic", "difficulty", "source", "created_by", "created_at")
    list_filter = ("topic", "difficulty", "source")
    search_fields = ("title", "statement", "tags")


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("problem", "user", "outcome", "started_at", "ended_at", "time_spent_seconds")
    list_filter = ("outcome", "user")
    search_fields = ("problem__title",)


@admin.register(MistakeType)
class MistakeTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Mistake)
class MistakeAdmin(admin.ModelAdmin):
    list_display = ("short_label", "mistake_type", "severity", "attempt")
    list_filter = ("mistake_type", "severity")
    search_fields = ("short_label", "detailed_postmortem")


@admin.register(ReviewItem)
class ReviewItemAdmin(admin.ModelAdmin):
    list_display = ("prompt", "user", "due_date", "interval_days", "ease_factor")
    list_filter = ("due_date", "user")
    search_fields = ("prompt",)
