from django.urls import path

from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("problems/", views.problem_list, name="problem_list"),
    path("problems/create/", views.problem_create, name="problem_create"),
    path("problems/<int:pk>/", views.problem_detail, name="problem_detail"),
    path("problems/<int:pk>/edit/", views.problem_edit, name="problem_edit"),
    path("attempts/", views.attempt_list, name="attempt_list"),
    path("attempts/start/<int:problem_id>/", views.start_attempt, name="start_attempt"),
    path("attempts/<int:pk>/finish/", views.finish_attempt, name="finish_attempt"),
    path(
        "attempts/<int:attempt_id>/mistakes/add/",
        views.add_mistake,
        name="add_mistake",
    ),
    path("mistakes/analytics/", views.mistake_analytics, name="mistake_analytics"),
    path("reviews/", views.review_queue, name="review_queue"),
    path("reviews/<int:pk>/grade/", views.grade_review, name="grade_review"),
    path("export/", views.export_data, name="export_data"),
    path("import/", views.import_data, name="import_data"),
]
