from django_project.budget.models import Budget


def get_user_budget_list_ordered_by_created_at(self, user):
        budgets = Budget.objects.filter(is_deleted=False, user=user).order_by("-created_at")
        return budgets