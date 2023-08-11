from datetime import timezone
from uuid import uuid4
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from .forms import BudgetForm, SignUpForm
from .models import Budget


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
        budgets = Budget.objects.order_by("-created_at")
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
        if form.is_valid():
            if not budget:
                budget = form.save(commit=False)
                budget.user = request.user
            budget = form.save()
            messages.success(
                request, f'Budget saved for {budget.purpose}!')
            return redirect('home')
        return render(request, 'setup_budget.html', {'form': form})
    else:
        messages.error(
            request, f'You must be logged in to set up a budget.', extra_tags='danger')
        return redirect(request, 'home')


def delete_budget(request, uuid):
    budget = get_object_or_404(Budget, uuid=uuid)
    budget.delete()
    messages.success(request, f'Budget deleted!')
    return redirect('home')


def budget_details(request, uuid):
    budget = Budget.objects.get(uuid=uuid)
    return render(request, 'budget_details.html', {'budget': budget})


def credits(request):
    return render(request, 'credits.html')
