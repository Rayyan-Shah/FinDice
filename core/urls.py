from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_transaction, name='add_transaction'),
    path('view/', views.view_transactions, name='view_transactions'),

]
