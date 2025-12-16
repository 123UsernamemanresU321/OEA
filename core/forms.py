from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Attempt, Mistake, Problem, ReviewItem


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ("username", "email")


class ProblemForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ["title", "source", "topic", "difficulty", "tags", "statement"]
        widgets = {
            "statement": forms.Textarea(
                attrs={"rows": 5, "class": "form-control latex-input", "id": "id_statement"}
            ),
            "difficulty": forms.NumberInput(attrs={"min": 1, "max": 10, "class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "source": forms.TextInput(attrs={"class": "form-control"}),
            "topic": forms.Select(attrs={"class": "form-select"}),
            "tags": forms.TextInput(attrs={"class": "form-control"}),
        }


class AttemptForm(forms.ModelForm):
    class Meta:
        model = Attempt
        fields = ["outcome", "final_answer", "solution_notes", "confidence"]
        widgets = {
            "final_answer": forms.Textarea(attrs={"rows": 3, "class": "form-control latex-input"}),
            "solution_notes": forms.Textarea(attrs={"rows": 4, "class": "form-control latex-input"}),
            "confidence": forms.NumberInput(attrs={"min": 1, "max": 5, "class": "form-control"}),
            "outcome": forms.Select(attrs={"class": "form-select"}),
        }


class MistakeForm(forms.ModelForm):
    class Meta:
        model = Mistake
        fields = [
            "mistake_type",
            "severity",
            "short_label",
            "detailed_postmortem",
            "conceptual_gap",
            "execution_error",
            "strategy_error",
            "fix_plan",
            "next_review_date",
        ]
        widgets = {
            "detailed_postmortem": forms.Textarea(
                attrs={"rows": 4, "class": "form-control latex-input"}
            ),
            "fix_plan": forms.Textarea(attrs={"rows": 3, "class": "form-control latex-input"}),
            "next_review_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "severity": forms.NumberInput(attrs={"min": 1, "max": 5, "class": "form-control"}),
            "mistake_type": forms.Select(attrs={"class": "form-select"}),
            "short_label": forms.TextInput(attrs={"class": "form-control"}),
            "conceptual_gap": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "execution_error": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "strategy_error": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class ReviewGradeForm(forms.Form):
    rating = forms.ChoiceField(
        choices=ReviewItem.RATING_CHOICES, widget=forms.RadioSelect, initial=ReviewItem.RATING_GOOD
    )


class ImportForm(forms.Form):
    file = forms.FileField()
