import datetime
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class CommonDataModel(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class SoftDeletableModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)
    deleted_by = models.ForeignKey(
        User, null=True, on_delete=models.CASCADE, related_name='%(class)s_deleted_by')

    class Meta:
        abstract = True

    def soft_delete(self, user_id=None):
        self.is_deleted = True
        self.deleted_by = user_id
        self.deleted_at = timezone.now()
        self.save()


class Budget(CommonDataModel, SoftDeletableModel):
    purpose = models.CharField(max_length=255, default=None)
    goal = models.DecimalField(max_digits=8, decimal_places=2, default=None)
    from_date = models.DateField(default=None)
    to_date = models.DateField(default=None)

    def __str__(self):
        return self.purpose

    def clean(self) -> None:
        super().clean()
        if self.from_date and self.to_date:
            if self.__class__.objects.filter(models.Q(from_date__lte=self.to_date, to_date__gte=self.from_date) | models.Q(from_date__lte=self.to_date, to_date__gte=self.to_date) | models.Q(from_date__gte=self.from_date, to_date__lte=self.to_date)).exclude(pk=self.pk).exists():
                raise ValueError(
                    'Budgeting period overlaps with another budgeting period')

    def overall_balance(self):
        total_income = Income.objects.filter(budget=self).aggregate(
            models.Sum('amount'))['amount__sum'] or 0
        total_expense = Expense.objects.filter(budget=self).aggregate(
            models.Sum('amount'))['amount__sum'] or 0
        return total_income - total_expense

    class Meta:
        verbose_name_plural = 'Budgets'


class Income(CommonDataModel, SoftDeletableModel):
    source = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.DateField()
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)

    def __str__(self):
        return self.source

    class Meta:
        verbose_name_plural = 'Income'


class Expense(CommonDataModel, SoftDeletableModel):
    source = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.DateField()
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)

    def __str__(self):
        return self.source

    class Meta:
        verbose_name_plural = 'Expenses'
