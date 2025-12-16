from django.db import migrations


def create_defaults(apps, schema_editor):
    MistakeType = apps.get_model("core", "MistakeType")
    defaults = [
        "Algebra slip",
        "Wrong lemma",
        "Invalid assumption",
        "Missed invariant",
        "Case bash explosion",
        "Time management",
    ]
    for name in defaults:
        MistakeType.objects.get_or_create(name=name, defaults={"description": name})


def reverse_defaults(apps, schema_editor):
    MistakeType = apps.get_model("core", "MistakeType")
    MistakeType.objects.filter(name__in=[
        "Algebra slip",
        "Wrong lemma",
        "Invalid assumption",
        "Missed invariant",
        "Case bash explosion",
        "Time management",
    ]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_defaults, reverse_defaults),
    ]
