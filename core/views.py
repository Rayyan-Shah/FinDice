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


from django.db.models import Sum
from datetime import date
from .models import UserProfile, Transaction, Budget
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def dashboard(request):
    user = request.user
    profile = UserProfile.objects.get(user=user)
    base_income = profile.income

    # Transactions
    recent_transactions = Transaction.objects.filter(user=user).order_by('-date')
    logged_income = Transaction.objects.filter(user=user, type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    expense_total = Transaction.objects.filter(user=user, type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    cash_total = Transaction.objects.filter(user=user, type='cash').aggregate(Sum('amount'))['amount__sum'] or 0

    total_income = base_income + logged_income
    net_total = total_income - expense_total

    # Budget: Get current month's budget
    today = date.today()
    current_month = date(today.year, today.month, 1)

    budget = Budget.objects.filter(
        user=user,
        month__year=today.year,
        month__month=today.month
    ).first()

    monthly_expenses = Transaction.objects.filter(
        user=user, type='expense',
        date__year=today.year,
        date__month=today.month
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    budget_left = budget.amount - monthly_expenses if budget else None
    try:
        financial_goal = FinancialGoal.objects.get(user=request.user)
    except FinancialGoal.DoesNotExist:
        financial_goal = None  # If the user doesn't have a goal, set it to None




    return render(request, 'dashboard.html', {
        'base_income': base_income,
        'logged_income': logged_income,
        'total_income': total_income,
        'expense_total': expense_total,
        'net_total': net_total,
        'cash_total': cash_total,
        'recent_transactions': recent_transactions,
        'budget': budget,
        'budget_left': budget_left,
        'monthly_expenses': monthly_expenses,
        'financial_goal': financial_goal,
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


# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import BudgetForm
from .models import Budget

@login_required
def set_budget(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user

            # Remove any existing budget for that month
            existing = Budget.objects.filter(user=request.user, month__year=budget.month.year, month__month=budget.month.month)
            if existing.exists():
                existing.delete()

            budget.save()
            return redirect('dashboard')  # or wherever you want
    else:
        form = BudgetForm()
    return render(request, 'set_budget.html', {'form': form})



# views.py
from django.shortcuts import render, redirect
from .forms import FinancialGoalForm
from .models import FinancialGoal

def set_financial_goal(request):
    if request.method == 'POST':
        form = FinancialGoalForm(request.POST)
        if form.is_valid():
            financial_goal = form.save(commit=False)
            financial_goal.user = request.user
            financial_goal.save()
            return redirect('dashboard')  # Redirect back to the dashboard
    else:
        form = FinancialGoalForm()
    return render(request, 'set_financial_goal.html', {'form': form})

# views.py
from django.shortcuts import render, redirect
from .forms import AddToSavingsForm
from .models import FinancialGoal

def add_to_savings(request):
    if request.method == 'POST':
        form = AddToSavingsForm(request.POST)
        if form.is_valid():
            financial_goal = FinancialGoal.objects.get(user=request.user)  # Get the user's financial goal
            amount_to_add = form.cleaned_data['current_savings']
            financial_goal.current_savings += amount_to_add  # Add the amount to current savings
            financial_goal.save()  # Save the updated goal
            return redirect('dashboard')  # Redirect to the dashboard after adding to savings
    else:
        form = AddToSavingsForm()
    return render(request, 'add_to_savings.html', {'form': form})




