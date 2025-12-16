from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django.core.validators
from datetime import date


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="MistakeType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
                ("description", models.TextField(blank=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Problem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("source", models.CharField(blank=True, max_length=200)),
                ("topic", models.CharField(choices=[("NT", "Number Theory"), ("ALG", "Algebra"), ("GEO", "Geometry"), ("COMB", "Combinatorics"), ("OTHER", "Other")], max_length=10)),
                ("difficulty", models.PositiveSmallIntegerField(default=5, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ("tags", models.CharField(blank=True, max_length=200)),
                ("statement", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Attempt",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("started_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("ended_at", models.DateTimeField(blank=True, null=True)),
                ("time_spent_seconds", models.PositiveIntegerField(default=0)),
                ("outcome", models.CharField(choices=[("solved", "Solved"), ("partial", "Partial"), ("stuck", "Stuck"), ("wrong", "Wrong")], default="stuck", max_length=20)),
                ("final_answer", models.TextField(blank=True)),
                ("solution_notes", models.TextField(blank=True)),
                ("confidence", models.PositiveSmallIntegerField(default=3, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ("problem", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attempts", to="core.problem")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-started_at"]},
        ),
        migrations.CreateModel(
            name="Mistake",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("severity", models.PositiveSmallIntegerField(default=3, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ("short_label", models.CharField(max_length=150)),
                ("detailed_postmortem", models.TextField()),
                ("conceptual_gap", models.BooleanField(default=False)),
                ("execution_error", models.BooleanField(default=False)),
                ("strategy_error", models.BooleanField(default=False)),
                ("fix_plan", models.TextField(blank=True)),
                ("next_review_date", models.DateField(blank=True, null=True)),
                ("attempt", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="mistakes", to="core.attempt")),
                ("mistake_type", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.mistaketype")),
            ],
            options={"ordering": ["-severity"]},
        ),
        migrations.CreateModel(
            name="ReviewItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("prompt", models.TextField()),
                ("answer_key", models.TextField()),
                ("ease_factor", models.FloatField(default=2.5)),
                ("interval_days", models.PositiveIntegerField(default=0)),
                ("due_date", models.DateField(default=date.today)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("related_mistake", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="reviews", to="core.mistake")),
                ("related_problem", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="reviews", to="core.problem")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["due_date"]},
        ),
    ]
