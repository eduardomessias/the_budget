from django.db import models
from django.contrib.auth.models import User


class Budget(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Income(models.Model):
    source = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.DateField()
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)

    def __str__(self):
        return self.source

    class Meta:
        verbose_name_plural = 'Income'


class Expense(models.Model):
    source = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.DateField()
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)

    def __str__(self):
        return self.source

    class Meta:
        verbose_name_plural = 'Expenses'
