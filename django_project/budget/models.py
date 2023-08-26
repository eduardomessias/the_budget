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
