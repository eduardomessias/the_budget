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
]
