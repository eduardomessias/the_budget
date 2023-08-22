from datetime import timezone
from uuid import uuid4
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from .forms import BudgetForm, ExpenseForm, IncomeForm, SignUpForm, BudgetEntryForm
from .models import Budget, Income, Expense


def home(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome {user.first_name}!')
            return redirect('home')
        else:
            messages.error(
                request, f'Error logging in as {username}. Please try again.', extra_tags='danger')
            return redirect('home')
    else:
        budgets = Budget.objects.filter(
            is_deleted=False).order_by("-created_at")
        return render(request, 'home.html', {'budgets': budgets})


def logout_user(request):
    logout(request)
    messages.info(request, f'You have been logged out.')
    return redirect('home')


def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password1 = form.cleaned_data['password1']
            user = authenticate(username=username, password=password1)
            login(request, user)
            messages.success(
                request, f'Account created for {user.first_name}!')
            return redirect('home')
    else:
        form = SignUpForm()
        return render(request, 'register.html', {'form': form})
    return render(request, 'register.html', {'form': form})


def setup_budget(request, uuid=None):
    if request.user.is_authenticated:
        budget = Budget.objects.get(uuid=uuid) if uuid else None
        form = BudgetForm(request.POST or None, instance=budget)
        try:
            if form.is_valid():
                if not budget:
                    budget = form.save(commit=False)
                    budget.user = request.user
                budget = form.save()
                messages.success(
                    request, f'Budget saved for {budget.purpose}!')
                return redirect('home')
            return render(request, 'setup_budget.html', {'form': form, 'budget': budget})
        except ValueError as e:
            messages.error(
                request, f'Error saving budget: {e}', extra_tags='danger')
            return render(request, 'setup_budget.html', {'form': form, 'budget': budget})
    else:
        messages.error(
            request, f'You must be logged in to set up a budget.', extra_tags='danger')
        return redirect(request, 'home')


def delete_budget(request, uuid):
    if request.user.is_authenticated:
        budget = get_object_or_404(Budget, uuid=uuid)
        budget.delete()
        messages.success(request, f'Budget deleted!')
        return redirect('home')
    else:
        messages.error(
            request, f'You must be logged in to delete a budget.', extra_tags='danger')
        return redirect(request, 'home')


def budget_details(request, uuid):
    if request.user.is_authenticated:
        budget = Budget.objects.get(uuid=uuid)
        return render(request, 'budget_details.html', {'budget': budget})
    else:
        messages.error(
            request, f'You must be logged in to view a budget.', extra_tags='danger')
        return redirect(request, 'home')


def budget_entries(request, uuid):
    if request.user.is_authenticated:
        budget = Budget.objects.get(uuid=uuid)
        incomes = Income.objects.filter(budget=budget, is_deleted=False)
        expenses = Expense.objects.filter(budget=budget, is_deleted=False)
        entries = incomes.union(expenses).order_by("-date")
        return render(request, 'budget_entries_list.html', {'budget': budget, 'entries': entries})
    else:
        messages.error(
            request, f'You must be logged in to view a budget.', extra_tags='danger')
        return redirect(request, 'home')


def register_income(request, uuid, income_uuid=None):
    if request.user.is_authenticated:
        budget = Budget.objects.get(uuid=uuid)
        income = Income.objects.get(uuid=income_uuid) if income_uuid else None
        form = IncomeForm(request.POST or None, instance=income)
        if form.is_valid():
            if not income:
                income = form.save(commit=False)
                income.user = request.user
                income.budget = budget
            income = form.save()
            messages.success(
                request, f'Income saved for {income.source}!')
            return redirect('budget_entries', uuid=uuid)
        return render(request, 'edit_budget_entry.html', {'form': form, 'budget': budget})
    else:
        messages.error(
            request, f'You must be logged in to register an income.', extra_tags='danger')
        return redirect(request, 'home')


def register_expense(request, uuid, expense_uuid=None):
    if request.user.is_authenticated:
        budget = Budget.objects.get(uuid=uuid)
        expense = Expense.objects.get(
            uuid=expense_uuid) if expense_uuid else None
        form = ExpenseForm(request.POST or None, instance=expense)
        if form.is_valid():
            if not expense:
                expense = form.save(commit=False)
                expense.user = request.user
                expense.budget = budget
                # make sure the amount is negative
                expense.amount = -expense.amount if expense.amount > 0 else expense.amount
            expense = form.save()
            messages.success(
                request, f'Expense saved for {expense.source}!')
            return redirect('budget_entries', uuid=uuid)
        return render(request, 'edit_budget_entry.html', {'form': form, 'budget': budget})
    else:
        messages.error(
            request, f'You must be logged in to register an expense.', extra_tags='danger')
        return redirect(request, 'home')


def delete_income(request, uuid, income_uuid):
    if request.user.is_authenticated:
        income = get_object_or_404(Income, uuid=income_uuid)
        income.soft_delete(request.user)
        messages.success(request, f'Income deleted!')
        return redirect('budget_entries', uuid=uuid)
    else:
        messages.error(
            request, f'You must be logged in to delete an income.', extra_tags='danger')
        return redirect(request, 'home')


def delete_expense(request, uuid, expense_uuid):
    if request.user.is_authenticated:
        expense = get_object_or_404(Expense, uuid=expense_uuid)
        expense.soft_delete(request.user)
        messages.success(request, f'Expense deleted!')
        return redirect('budget_entries', uuid=uuid)
    else:
        messages.error(
            request, f'You must be logged in to delete an expense.', extra_tags='danger')
        return redirect(request, 'home')


def income_details(request, uuid, entry_uuid):
    if request.user.is_authenticated:
        budget = Budget.objects.get(uuid=uuid)
        income = Income.objects.get(uuid=entry_uuid)
        return render(request, 'income_details.html', {'budget': budget, 'income': income})
    else:
        messages.error(
            request, f'You must be logged in to view an income.', extra_tags='danger')
        return redirect(request, 'home')


def expense_details(request, uuid, entry_uuid):
    if request.user.is_authenticated:
        budget = Budget.objects.get(uuid=uuid)
        expense = Expense.objects.get(uuid=entry_uuid)
        return render(request, 'expense_details.html', {'budget': budget, 'expense': expense})
    else:
        messages.error(
            request, f'You must be logged in to view an expense.', extra_tags='danger')
        return redirect(request, 'home')


def credits(request):
    return render(request, 'credits.html')
