from datetime import date

from .models import ReviewItem


def analytics_counts(request):
    if not request.user.is_authenticated:
        return {}
    due_reviews = ReviewItem.objects.filter(user=request.user, due_date__lte=date.today()).count()
    return {"nav_due_reviews": due_reviews}
