from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("credits/", views.credits, name="credits"),
    path("logout/", views.logout_user, name="logout"),
    path("register/", views.register_user, name="register"),
    path("<uuid:uuid>/", views.budget_details, name="budget_details"),
    path("setup_budget/", views.setup_budget, name="setup_budget"),
    path("setup_budget/<uuid:uuid>/", views.setup_budget, name="setup_budget"),
    path("delete_budget/<uuid:uuid>/", views.delete_budget, name="delete_budget"),
    path("budget_entries/<uuid:uuid>/",
         views.budget_entries, name="budget_entries"),
    path("register_income/<uuid:uuid>/",
         views.register_income, name="register_income"),
    path("register_income/<uuid:uuid>/<uuid:income_uuid>/",
         views.register_income, name="register_income"),
    path("register_expense/<uuid:uuid>/",
         views.register_expense, name="register_expense"),
    path("register_expense/<uuid:uuid>/<uuid:expense_uuid>/",
         views.register_expense, name="register_expense"),
    path("delete_income/<uuid:uuid>/<uuid:income_uuid>/",
         views.delete_income, name="delete_income"),
    path("delete_expense/<uuid:uuid>/<uuid:expense_uuid>/",
         views.delete_expense, name="delete_expense"),
    path("income_details/<uuid:uuid>/<uuid:entry_uuid>/",
         views.income_details, name="income_details"),
    path("expense_details/<uuid:uuid>/<uuid:entry_uuid>/",
         views.expense_details, name="expense_details"),
    path("load_recurrencies/<uuid:uuid>/",
         name="load_recurrencies", view=views.load_recurrencies),
]
