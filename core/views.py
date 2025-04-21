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


from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Transaction
from django.shortcuts import render
from .models import Transaction
from django.core.paginator import Paginator
from datetime import datetime

@login_required
def view_transactions(request):
    # Get the category filter value from the GET request (default to 'all' if not provided)
    category_filter = request.GET.get('category', 'all')

    # Get the date filter values from the GET request (default to None if not provided)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Start building the query filter
    transactions = Transaction.objects.filter(user=request.user)

    # Apply category filter if provided
    if category_filter != 'all':
        transactions = transactions.filter(category=category_filter)

    # Apply date range filter if both start_date and end_date are provided
    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    if end_date:
        transactions = transactions.filter(date__lte=end_date)

    # Sort the transactions by date (most recent first)
    transactions = transactions.order_by('-date')

    # Paginate the transactions (10 per page)
    paginator = Paginator(transactions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get the list of categories for the dropdown
    categories = Transaction.CATEGORY_CHOICES

    return render(request, 'view_transactions.html', {
        'page_obj': page_obj,  # Pass the paginated transactions
        'categories': categories,  # Pass the categories for the dropdown
        'category_filter': category_filter,  # Pass the selected category filter
        'start_date': start_date,  # Pass the selected start date
        'end_date': end_date,  # Pass the selected end date
    })



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


import csv
from django.http import HttpResponse
from .models import Transaction  # Update with the correct model import


def download_csv(request):
    # Get the transactions (you can add filters here if needed)
    transactions = Transaction.objects.all()  # Or apply filters based on request.GET data

    # Create the HttpResponse with CSV content
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'

    writer = csv.writer(response)

    # Write header row
    writer.writerow(['Amount', 'Type', 'Category', 'Description', 'Date'])

    # Write each transaction row
    for transaction in transactions:
        writer.writerow([transaction.amount, transaction.get_type_display(), transaction.get_category_display(),
                         transaction.description, transaction.date])

    return response


# views.py


# views.py

import matplotlib

matplotlib.use('Agg')  # Ensure Matplotlib runs in a non-interactive mode suitable for web servers
import matplotlib.pyplot as plt
import io
import base64
from django.shortcuts import render
from django.db.models import Sum
from .models import Transaction
import calendar
from datetime import datetime

from datetime import datetime
import calendar
import io
import base64
import matplotlib.pyplot as plt
from django.shortcuts import render
from django.db.models import Sum
from .models import Transaction, Budget, FinancialGoal


def view_reports(request):
    # Retrieve expenses data by category
    transactions = Transaction.objects.filter(user=request.user)
    expense_categories = transactions.filter(type='expense').values('category').annotate(total_amount=Sum('amount'))

    # Pie chart for expenses by category
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie([cat['total_amount'] for cat in expense_categories],
           labels=[cat['category'] for cat in expense_categories],
           autopct='%1.1f%%',
           startangle=140)
    ax.set_title("Expenses by Category")
    plt.tight_layout()

    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)
    img_data = base64.b64encode(img_buf.read()).decode('utf-8')
    plt.close(fig)

    # Line graph for total income per month this year
    current_year = datetime.now().year
    months = [calendar.month_name[i] for i in range(1, 13)]
    total_income_per_month = []

    for month in range(1, 13):
        total_income = transactions.filter(
            type='income',
            date__year=current_year,
            date__month=month
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        total_income_per_month.append(total_income)

    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.plot(months, total_income_per_month, marker='o', linestyle='-', color='b')
    ax2.set_title("Total Income per Month (This Year)")
    ax2.set_xlabel('Month')
    ax2.set_ylabel('Income ($)')
    ax2.tick_params(axis='x', rotation=45)
    plt.tight_layout()

    img_buf2 = io.BytesIO()
    plt.savefig(img_buf2, format='png')
    img_buf2.seek(0)
    income_img_data = base64.b64encode(img_buf2.read()).decode('utf-8')
    plt.close(fig2)

    # Get budget and goal objects
    budget = Budget.objects.filter(user=request.user).first()
    goal = FinancialGoal.objects.filter(user=request.user).first()

    # Generate dynamic summary text
    dynamic_text = f"""
    <p>This report summarizes the user's financial activity over the current calendar year, highlighting key trends in income and expenses. The data includes monthly income distributions and categorized expenditures, offering a foundation for ongoing financial planning and evaluation.</p>

    <p>The income chart reveals significant variability throughout the year. For example, the user earned ${total_income_per_month[0]:,.2f} in {months[0]}, followed by fluctuations that led to a peak of ${total_income_per_month[5]:,.2f} in {months[5]}. These figures may reflect seasonal employment, variable business performance, or other external income influences. Recognizing these cycles is essential for forecasting future income and improving financial stability.</p>

    <p>Expense analysis shows a concentration of spending within specific categories. The pie chart outlines how funds are distributed, enabling users to visually identify their most significant expense areas. This can support targeted interventions, such as reducing discretionary spending or negotiating recurring costs. Notably, {months[3]} and {months[9]} showed elevated expense levels, which may correspond to irregular but expected costs such as tuition, travel, or holidays.</p>

    <p>The user's budget is currently set at ${budget.amount if budget else 'N/A'}. Budget tracking ensures spending stays aligned with goals and income, and users may benefit from revisiting this figure periodically based on changing needs or financial goals. Creating sub-budgets per category could further enhance visibility and control.</p>

    <p>Progress toward the user’s financial goal is also reflected in this report. With current savings totaling ${goal.current_savings if goal else 'N/A'} and a target of ${goal.target_amount if goal else 'N/A'}, consistent contributions remain key. Users are encouraged to align savings with high-income months to accelerate goal achievement, particularly if income continues to fluctuate across the year.</p>

    <p>In summary, the data suggests that financial behavior is dynamic, shaped by both recurring habits and external conditions. By continuing to monitor monthly changes and category-level trends, users can proactively adapt strategies to reduce unnecessary spending, increase savings, and move closer to long-term objectives.</p>
    """


    return render(request, 'view_reports.html', {
        'img_data': img_data,
        'income_img_data': income_img_data,
        'dynamic_text': dynamic_text,
    })
