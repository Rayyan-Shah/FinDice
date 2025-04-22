from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Home + Dashboard
    path('', views.home, name='home'),

    path('dashboard/', views.dashboard, name='dashboard'),

    # Auth
    path('register/', views.register, name='register'),
    path('learn/',views.learn, name='learn'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    # Password Reset
    path('reset-password/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('reset-password-done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),

    # Transaction Views
    path('transactions/add/', views.add_transaction, name='add_transaction'),
    path('transactions/view/', views.view_transactions, name='view_transactions'),
path('budget/', views.set_budget, name='set_budget'),
path('set_financial_goal/', views.set_financial_goal, name='set_financial_goal'),

    path('add_to_savings/', views.add_to_savings, name='add_to_savings'),
    path('download-csv/', views.download_csv, name='download_csv'),

path('reports/', views.view_reports, name='view_reports'),
    path('account/', views.account_settings, name='account_settings'),
    # other paths


]
