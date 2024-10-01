import datetime
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from dateutil import relativedelta


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
        total_income = Income.objects.filter(budget=self, is_deleted=False).aggregate(
            models.Sum('amount'))['amount__sum'] or 0
        total_expense = Expense.objects.filter(budget=self, is_deleted=False).aggregate(
            models.Sum('amount'))['amount__sum'] or 0
        return total_income + total_expense

    def reload_recurrencies(self):
        incomes = Income.objects.filter(is_recurrent=True, is_deleted=False)
        expenses = Expense.objects.filter(is_recurrent=True, is_deleted=False)
        for income in incomes:
            income_last_recurrency_date = income.last_recurrency_date()
            if income_last_recurrency_date >= self.from_date:
                income.create_recurrencies()
        for expense in expenses:
            expense_last_recurrency_date = expense.last_recurrency_date()
            if expense_last_recurrency_date >= self.from_date:
                expense.create_recurrencies()

    class Meta:
        verbose_name_plural = 'Budgets'


class RecurrencyType(models.TextChoices):
    ONE_OFF = 0
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3
    YEARLY = 4


class Income(CommonDataModel, SoftDeletableModel):
    source = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.DateField()
    is_recurrent = models.BooleanField(default=False)
    recurrency = models.CharField(
        max_length=10, choices=RecurrencyType.choices, default=RecurrencyType.ONE_OFF)
    frequency = models.IntegerField(default=1)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.source

    def clean(self) -> None:
        super().clean()
        if self.date and self.budget:
            if self.date < self.budget.from_date or self.date > self.budget.to_date:
                raise ValueError(
                    F'Income date is not within the budgeting period (from {self.budget.from_date} to {self.budget.to_date})')

    def last_recurrency_date(self):
        if self.recurrency == RecurrencyType.DAILY:
            return self.date + relativedelta.relativedelta(days=self.frequency)
        elif self.recurrency == RecurrencyType.WEEKLY:
            return self.date + relativedelta.relativedelta(weeks=self.frequency)
        elif self.recurrency == RecurrencyType.MONTHLY:
            return self.date + relativedelta.relativedelta(months=self.frequency)
        elif self.recurrency == RecurrencyType.YEARLY:
            return self.date + relativedelta.relativedelta(years=self.frequency)

    def next_recurrency_date(self, date):
        if self.recurrency == RecurrencyType.DAILY:
            return date + relativedelta.relativedelta(days=1)
        elif self.recurrency == RecurrencyType.WEEKLY:
            return date + relativedelta.relativedelta(weeks=1)
        elif self.recurrency == RecurrencyType.MONTHLY:
            return date + relativedelta.relativedelta(months=1)
        elif self.recurrency == RecurrencyType.YEARLY:
            return date + relativedelta.relativedelta(years=1)
        return date

    def create_recurrency(self, date, ocurrence, series):
        child = Income()
        child.budget = self.budget
        child.user = self.user
        child.parent = self
        child.source = f'{self.source} ({ocurrence} of {series})'
        child.amount = self.amount
        child.is_recurrent = False
        child.frequency = 1
        child.recurrency = RecurrencyType.ONE_OFF
        child.date = date
        if child.date <= self.budget.to_date:
            child.save()
        elif child.date > self.budget.to_date:
            existing_budget = Budget.objects.filter(
                from_date__lte=child.date, to_date__gte=child.date).first()
            if existing_budget:
                child.budget = existing_budget
                child.save()

    def create_recurrencies(self):
        Income.objects.filter(parent=self).update(
            is_deleted=True, deleted_by=self.user)
        if self.is_recurrent:
            date = self.date
            for i in range(2, self.frequency + 1):
                date = self.next_recurrency_date(date)
                self.create_recurrency(date, i, self.frequency)

    class Meta:
        verbose_name_plural = 'Income'


class Expense(CommonDataModel, SoftDeletableModel):
    source = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.DateField()
    is_recurrent = models.BooleanField(default=False)
    recurrency = models.CharField(
        max_length=10, choices=RecurrencyType.choices, default=RecurrencyType.MONTHLY)
    frequency = models.IntegerField(default=1)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.source

    def clean(self) -> None:
        super().clean()
        if self.date and self.budget:
            if self.date < self.budget.from_date or self.date > self.budget.to_date:
                raise ValueError(
                    F'Expense date is not within the budgeting period (from {self.budget.from_date} to {self.budget.to_date})')

    def last_recurrency_date(self):
        if self.recurrency == RecurrencyType.DAILY:
            return self.date + relativedelta.relativedelta(days=self.frequency)
        elif self.recurrency == RecurrencyType.WEEKLY:
            return self.date + relativedelta.relativedelta(weeks=self.frequency)
        elif self.recurrency == RecurrencyType.MONTHLY:
            return self.date + relativedelta.relativedelta(months=self.frequency)
        elif self.recurrency == RecurrencyType.YEARLY:
            return self.date + relativedelta.relativedelta(years=self.frequency)
        return self.date

    def next_recurrency_date(self, date):
        if self.recurrency == RecurrencyType.DAILY:
            return date + relativedelta.relativedelta(days=1)
        elif self.recurrency == RecurrencyType.WEEKLY:
            return date + relativedelta.relativedelta(weeks=1)
        elif self.recurrency == RecurrencyType.MONTHLY:
            return date + relativedelta.relativedelta(months=1)
        elif self.recurrency == RecurrencyType.YEARLY:
            return date + relativedelta.relativedelta(years=1)
        return date

    def create_recurrency(self, date, ocurrence, series):
        child = Expense()
        child.budget = self.budget
        child.user = self.user
        child.parent = self
        child.source = f'{self.source} ({ocurrence} of {series})'
        child.amount = self.amount
        child.is_recurrent = False
        child.frequency = 1
        child.recurrency = RecurrencyType.ONE_OFF
        child.date = date
        if child.date <= self.budget.to_date:
            child.save()
        elif child.date > self.budget.to_date:
            existing_budget = Budget.objects.filter(
                from_date__lte=child.date, to_date__gte=child.date).first()
            if existing_budget:
                child.budget = existing_budget
                child.save()

    def create_recurrencies(self):
        # Excluindo a despesa atual
        Expense.objects.filter(parent=self).update(
            is_deleted=True, deleted_by=self.user)

        # Verifica se é recorrente
        if self.is_recurrent:
            date = self.date
            for i in range(2, self.frequency + 1):
                date = self.next_recurrency_date(date)
                self.create_recurrency(date, i, self.frequency)

    class Meta:
        verbose_name_plural = 'Expenses'
