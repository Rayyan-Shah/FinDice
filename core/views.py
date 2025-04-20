from django.db.models import Sum
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import TransactionForm
from .models import Transaction, UserProfile
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm  # Make sure this is imported
from django.contrib import messages
def home(request):
    return render(request, 'home.html')



def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)  # Use your custom form
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "You have successfully registered!")
            return redirect('dashboard')  # Redirect to the dashboard or desired page
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})


@login_required
def dashboard(request):
    base_income = UserProfile.objects.get(user=request.user).income
    recent_transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    # Total income from "income"-type transactions
    logged_income = Transaction.objects.filter(user=request.user, type='income').aggregate(Sum('amount'))['amount__sum'] or 0

    # Total expenses
    expense_total = Transaction.objects.filter(user=request.user, type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    cash_total = Transaction.objects.filter(user=request.user, type='cash').aggregate(Sum('amount'))['amount__sum'] or 0

    # Combined total income
    total_income = base_income + logged_income

    # Net = total income - expenses
    net_total = total_income - expense_total

    return render(request, 'dashboard.html', {
        'base_income': base_income,
        'logged_income': logged_income,
        'total_income': total_income,
        'expense_total': expense_total,
        'net_total': net_total,
        'cash_total': cash_total,
        'recent_transactions': recent_transactions,
    })


@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, "✅ Transaction added successfully!")
            return redirect('add_transaction')  # redirect avoids resubmission
    else:
        form = TransactionForm()

    return render(request, 'add_transaction.html', {'form': form})


@login_required
def view_transactions(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')[:10]
    print(f"Transactions for {request.user.username}: {transactions.count()} found.")
    return render(request, 'view_transactions.html', {'transactions': transactions})


def learn(request):
    return render(request, 'learn.html')