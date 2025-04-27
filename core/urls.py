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

    path('reset-password/', views.reset_password_email, name='reset_password_email'),
    path('set-new-password/', views.set_new_password, name='set_new_password'),
    # Transaction Views
    path('transactions/add/', views.add_transaction, name='add_transaction'),
    path('transactions/view/', views.view_transactions, name='view_transactions'),
path('budget/', views.set_budget, name='set_budget'),
path('set_financial_goal/', views.set_financial_goal, name='set_financial_goal'),

    path('add_to_savings/', views.add_to_savings, name='add_to_savings'),
    path('download-csv/', views.download_csv, name='download_csv'),

path('reports/', views.view_reports, name='view_reports'),
    path('account/', views.account_settings, name='account_settings'),
path('create_link_token/', views.create_link_token, name='create_link_token'),
    path('exchange_public_token/', views.exchange_public_token, name='exchange_public_token'),
path('fetch_transactions/', views.fetch_transactions, name='fetch_transactions'),

    # other paths


]
