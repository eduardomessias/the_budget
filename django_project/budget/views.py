from django.utils import timezone
from uuid import uuid4
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from dateutil import relativedelta

from .forms import BudgetForm, ExpenseForm, IncomeForm, SignUpForm, CategoryForm
from .models import Budget, Income, Expense, RecurrencyType, Category


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
        active_budget = Budget.objects.filter(
            is_deleted=False, from_date__lte=timezone.now(), to_date__gte=timezone.now()).first()
        return render(request, 'home.html', {'budgets': budgets, 'active_budget': active_budget})


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
                budget.reload_recurrencies()
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
        income = Income.objects.get(
            uuid=income_uuid) if income_uuid else Income()
        income.budget = budget
        income.user = request.user
        form = IncomeForm(request.POST or None, instance=income)
        try:
            if form.is_valid():
                if not income:
                    income = form.save(commit=False)
                income.is_recurrent = True if income.frequency > 1 else False
                income = form.save()
                income.create_recurrencies()
                messages.success(request, f'Income saved for {income.source}!')
                return redirect('budget_entries', uuid=uuid)
            return render(request, 'edit_budget_entry.html', {'form': form, 'budget': budget})
        except ValueError as e:
            messages.error(
                request, f'Error saving income: {e}', extra_tags='danger')
            return render(request, 'edit_budget_entry.html', {'form': form, 'budget': budget})
    else:
        messages.error(
            request, f'You must be logged in to register an income.', extra_tags='danger')
        return redirect(request, 'home')


def register_expense(request, uuid, expense_uuid=None):
    if request.user.is_authenticated:
        budget = Budget.objects.get(uuid=uuid)
        expense = Expense.objects.get(
            uuid=expense_uuid) if expense_uuid else Expense()
        expense.budget = budget
        expense.user = request.user
        form = ExpenseForm(request.POST or None, instance=expense)
        try:
            if form.is_valid():
                if not expense:
                    expense = form.save(commit=False)
                # make sure the amount is negative
                expense.amount = -expense.amount if expense.amount >= 0 else expense.amount
                expense.is_recurrent = True if expense.frequency > 1 else False
                expense = form.save()
                expense.create_recurrencies()
                messages.success(
                    request, f'Expense saved for {expense.source}!')
                return redirect('budget_entries', uuid=uuid)
            return render(request, 'edit_budget_entry.html', {'form': form, 'budget': budget})
        except ValueError as e:
            messages.error(
                request, f'Error saving expense: {e}', extra_tags='danger')
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
        income.recurrency = RecurrencyType(income.recurrency).label
        return render(request, 'income_details.html', {'budget': budget, 'income': income})
    else:
        messages.error(
            request, f'You must be logged in to view an income.', extra_tags='danger')
        return redirect(request, 'home')


def expense_details(request, uuid, entry_uuid):
    if request.user.is_authenticated:
        budget = Budget.objects.get(uuid=uuid)
        expense = Expense.objects.get(uuid=entry_uuid)
        expense.recurrency = RecurrencyType(expense.recurrency).label
        return render(request, 'expense_details.html', {'budget': budget, 'expense': expense})
    else:
        messages.error(
            request, f'You must be logged in to view an expense.', extra_tags='danger')
        return redirect(request, 'home')


def load_recurrencies(request, uuid):
    if request.user.is_authenticated:
        try:
            budget = Budget.objects.get(uuid=uuid)
            load_expense_recurrencies(request, budget)
            load_income_recurrencies(request, budget)
            messages.info(request, f'Recurrencies loaded!')
            return redirect('budget_entries', uuid=uuid)
        except ValueError as e:
            messages.error(
                request, f'Error loading recurrencies: {e}', extra_tags='danger')
            return redirect('budget_entries', uuid=uuid)
    else:
        messages.error(
            request, f'You must be logged load recurrencies into this budget.', extra_tags='danger')
        return redirect(request, 'home')


def load_income_recurrencies(request, budget):
    incomes = Income.objects.filter(is_recurrent=True, is_deleted=False)
    for income in incomes:
        income_last_recurrency_date = income.last_recurrency_date()
        if income_last_recurrency_date >= budget.from_date:
            income.create_recurrencies()


def load_expense_recurrencies(request, budget):
    expenses = Expense.objects.filter(is_recurrent=True, is_deleted=False)
    for expense in expenses:
        expense_last_recurrency_date = expense.last_recurrency_date()
        if expense_last_recurrency_date >= budget.from_date:
            expense.create_recurrencies()


def credits(request):
    return render(request, 'credits.html')

def user_settings(request):
    if request.user.is_authenticated:                        
        return render(request, 'user_settings.html')
    else:
        messages.error(
            request, f'You must be logged in to view the settings.', extra_tags='danger')
        return redirect(request, 'home')

def categories(request):
    if request.user.is_authenticated: 
        categories = Category.objects.all()           
        return render(request, 'categories.html', {'categories': categories})
    else:
        messages.error(
            request, f'You must be logged in to edit categories.', extra_tags='danger')
        return redirect(request, 'home')
   
def add_category(request):
    if request.user.is_authenticated:        
        category = Category()  
        category.user = request.user
        form = CategoryForm(request.POST or None, instance=category)
        try:
            if form.is_valid():
                if not category:
                    category = form.save(commit=False)                
                category = form.save()                
                messages.success(request, f'Category added {category.category}!')
                return redirect('categories')
            return render(request, 'edit_category.html', {'form': form})
        except ValueError as e:
            messages.error(
                request, f'Error saving category: {e}', extra_tags='danger')
            return render(request, 'edit_category.html', {'form': form})
    else:
        messages.error(
            request, f'You must be logged in to add a category.', extra_tags='danger')
        return redirect(request, 'home')
    
def edit_category(request, category_id):
    if request.user.is_authenticated:
        try:
            category = Category.objects.get(id=category_id, user=request.user)
            #category.user = request.user
        except Category.DoesNotExist:
            messages.error(request, 'Category not found or access denied.', extra_tags='danger')
            return redirect('categories')

        form = CategoryForm(request.POST or None, instance=category)
        
        if request.method == 'POST':
            try:
                if form.is_valid():
                    category = form.save()
                    messages.success(request, f'Category updated to {category.category}!')
                    return redirect('categories')
            except ValueError as e:
                messages.error(request, f'Error updating category: {e}', extra_tags='danger')

        return render(request, 'edit_category.html', {'form': form, 'category': category})
    else:
        messages.error(request, 'You must be logged in to edit a category.', extra_tags='danger')
        return redirect('home')

def remove_category(request, uuid):
    if request.user.is_authenticated:
        try:
            category = Category.objects.get(uuid=uuid, user=request.user)
            category_name = category.name  # Store the category name for the message
            category.delete()
            messages.success(request, f'Category "{category_name}" has been successfully removed!')
            return redirect('categories')
        except Category.DoesNotExist:
            messages.error(request, 'Category not found or access denied.', extra_tags='danger')
            return redirect('categories')
    else:
        messages.error(request, 'You must be logged in to remove a category.', extra_tags='danger')
        return redirect('home')