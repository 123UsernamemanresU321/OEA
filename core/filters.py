import django_filters

from .models import Problem, TOPIC_CHOICES


class ProblemFilter(django_filters.FilterSet):
    topic = django_filters.MultipleChoiceFilter(choices=TOPIC_CHOICES)
    difficulty_min = django_filters.NumberFilter(field_name="difficulty", lookup_expr="gte")
    difficulty_max = django_filters.NumberFilter(field_name="difficulty", lookup_expr="lte")
    tags = django_filters.CharFilter(field_name="tags", lookup_expr="icontains")
    source = django_filters.CharFilter(field_name="source", lookup_expr="icontains")

    class Meta:
        model = Problem
        fields = ["topic", "difficulty", "tags", "source"]
