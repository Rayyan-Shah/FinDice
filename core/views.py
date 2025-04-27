from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from datetime import date, datetime
import json, os, csv, calendar, io, base64
import matplotlib
matplotlib.use('Agg')  # For server-side Matplotlib
import matplotlib.pyplot as plt
from openai import OpenAI
from .forms import (
    TransactionForm, CustomUserCreationForm, BudgetForm,
    FinancialGoalForm, AddToSavingsForm, AccountSettingsForm
)
from .models import (
    Transaction, UserProfile, Budget, FinancialGoal,
    APIConfig, SystemPrompt
)
from django.contrib import messages


# ---------------------------Views------------------------

def home(request):
    return render(request, 'home.html', {'hide_navbar': True})

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
    user = request.user
    if user.is_staff or user.is_superuser:
        base_income = 0
        profile = None
    else:
        profile, created = UserProfile.objects.get_or_create(user=user, defaults={'income': 0})
        base_income = profile.income

    # Transactions
    recent_transactions = Transaction.objects.filter(user=user).order_by('-date')[:10]
    logged_income = Transaction.objects.filter(user=user, type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    expense_total = Transaction.objects.filter(user=user, type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    cash_total = Transaction.objects.filter(user=user, type='cash').aggregate(Sum('amount'))['amount__sum'] or 0

    total_income = base_income + logged_income
    net_total = total_income - expense_total

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

    # Financial goal
    try:
        financial_goal = FinancialGoal.objects.get(user=request.user)
    except FinancialGoal.DoesNotExist:
        financial_goal = None

    budget_warning = None

    if budget:
        budget_usage_percentage = (monthly_expenses / budget.amount) * 100

        if budget_usage_percentage >= 100:
            budget_warning = "You have exceeded your monthly budget!"
        elif budget_usage_percentage >= 80:
            budget_warning = "You are nearing your monthly budget (over 80% used)!"

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
        'budget_warning': budget_warning,
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
    category_filter = request.GET.get('category', 'all')

    start_date = request.GET.get('start_date')
    if not start_date or start_date == 'None':
        start_date = None

    end_date = request.GET.get('end_date')
    if not end_date or end_date == 'None':
        end_date = None

    transactions = Transaction.objects.filter(user=request.user)

    if category_filter != 'all':
        transactions = transactions.filter(category=category_filter)

    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    if end_date:
        transactions = transactions.filter(date__lte=end_date)

    transactions = transactions.order_by('-date')

    paginator = Paginator(transactions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Transaction.CATEGORY_CHOICES

    return render(request, 'view_transactions.html', {
        'page_obj': page_obj,
        'categories': categories,
        'category_filter': category_filter,
        'start_date': start_date,
        'end_date': end_date,
    })


def learn(request):
    return render(request, 'learn.html')

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



@login_required
def set_financial_goal(request):
    try:
        financial_goal = FinancialGoal.objects.get(user=request.user)
    except FinancialGoal.DoesNotExist:
        financial_goal = None

    if request.method == 'POST':
        form = FinancialGoalForm(request.POST, instance=financial_goal)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user  # Ensure user is set
            goal.save()
            return redirect('dashboard')
    else:
        form = FinancialGoalForm(instance=financial_goal)

    return render(request, 'set_financial_goal.html', {'form': form})





@login_required
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



@login_required
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



def get_api_key(service_name="SAMBANOVA"):
    try:
        config = APIConfig.objects.get(service_name=service_name)
        return config.api_key
    except APIConfig.DoesNotExist:
        return None



from django.db.models import Sum
import calendar
from datetime import datetime
from openai import OpenAI
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Transaction, Budget, FinancialGoal, UserProfile, APIConfig

@login_required
@csrf_exempt
def view_reports(request):
    user = request.user
    transactions = Transaction.objects.filter(user=user)

    # Expenses by Category
    expense_categories = transactions.filter(type='expense') \
        .values('category') \
        .annotate(total_amount=Sum('amount'))
    pie_data = [['Category', 'Amount']]
    for item in expense_categories:
        pie_data.append([item['category'], float(item['total_amount'])])

    # Line graph: Income per Month
    current_year = datetime.now().year
    months = [calendar.month_abbr[i] for i in range(1, 13)]
    line_data = [['Month', 'Income']]
    for month_num in range(1, 13):
        monthly_income = transactions.filter(
            type='income',
            date__year=current_year,
            date__month=month_num
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        line_data.append([calendar.month_abbr[month_num], float(monthly_income)])

    # Budget and Financial Goal
    budget = Budget.objects.filter(user=user, month__year=current_year, month__month=datetime.now().month).first()
    goal = FinancialGoal.objects.filter(user=user).first()

    # Basic dynamic text for the page
    dynamic_text = """
    <p>This report summarizes your financial activity over the current calendar year, highlighting trends in income and expenses.</p>
    """

    # --- Build the user's personal financial snapshot ---
    profile = UserProfile.objects.filter(user=user).first()
    base_income = profile.income if profile else 0
    logged_income = transactions.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    expenses_total = transactions.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    cash_total = transactions.filter(type='cash').aggregate(Sum('amount'))['amount__sum'] or 0
    total_income = base_income + logged_income
    budget_amount = budget.amount if budget else "No budget set"
    savings_progress = goal.get_progress_percentage() if goal else "No financial goal set"

    # Keyword analysis based on description
    keywords = ['toys', 'games', 'clothes', 'gifts', 'travel', 'electronics', 'food', 'rent', 'entertainment']
    keyword_spending = {k: 0 for k in keywords}
    for t in transactions.filter(type='expense'):
        if t.description:
            for k in keywords:
                if k in t.description.lower():
                    keyword_spending[k] += float(t.amount)

    # Build the user snapshot
    user_name = user.first_name or user.username
    user_snapshot = f"""
You are assisting {user_name} (Username: {user.username}).

🧾 Income and Expenses:
- Base Income: ${base_income:.2f}
- Logged Income: ${logged_income:.2f}
- Cash Total: ${cash_total:.2f}
- Expenses Total: ${expenses_total:.2f}
- Total Income (Base + Logged): ${total_income:.2f}

📊 Budget and Financial Goals:
- Current Month's Budget: {budget_amount}
- Financial Goal Progress: {savings_progress if isinstance(savings_progress, str) else f"{savings_progress:.2f}%"}

🗂️ Expense Categories:
"""
    for item in expense_categories:
        user_snapshot += f"   - {item['category'].capitalize()}: ${item['total_amount']:.2f}\n"

    user_snapshot += "\n🔍 Spending by Description Keywords:\n"
    for keyword, amount in keyword_spending.items():
        if amount > 0:
            user_snapshot += f"   - {keyword.capitalize()}: ${amount:.2f}\n"

    # --- Retrieve Admin System Prompt (if any) ---
    prompt_obj = SystemPrompt.objects.first()
    admin_prompt = prompt_obj.content.strip() if prompt_obj else None

    if admin_prompt:
        final_system_prompt = admin_prompt + "\n\n" + user_snapshot
    else:
        # Default fallback if no admin custom prompt
        final_system_prompt = f"""
Hi {user_name}! 👋 I'm your personal finance assistant.
Here is your financial snapshot:

{user_snapshot}

Please ask me anything about your spending, savings, or budgeting! I'll keep my answers short, clear, and helpful.
        """.strip()

    # Debug (optional)
    print("🧠 Final System Prompt sent to AI:\n", final_system_prompt)

    # --- Handle Chat POST AJAX ---
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        user_message = request.POST.get('user_message')
        try:
            api_key = get_api_key('SAMBANOVA')

            if not api_key:
                return JsonResponse({'response': "❌ API key not configured. Please contact admin."}, status=500)

            client = OpenAI(
                api_key=api_key,
                base_url="https://api.sambanova.ai/v1/",
            )

            model = "DeepSeek-V3-0324"

            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": final_system_prompt},
                    {"role": "user", "content": user_message},
                ],
                stream=True,
            )

            ai_response = ""
            for chunk in completion:
                ai_response += chunk.choices[0].delta.content or ""

            return JsonResponse({'response': ai_response})

        except Exception as e:
            return JsonResponse({'response': f"❌ Error: {str(e)}"}, status=500)

    # --- Normal page load (GET) ---
    context = {
        'pie_data': pie_data,
        'line_data': line_data,
        'dynamic_text': dynamic_text,
    }
    return render(request, 'view_reports.html', context)


@login_required
def account_settings(request):
    if request.method == 'POST':
        form = AccountSettingsForm(request.POST, instance=request.user, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Your account has been updated!")
            return redirect('dashboard')
    else:
        form = AccountSettingsForm(instance=request.user, user=request.user)

    return render(request, 'account_settings.html', {'form': form})

# core/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .plaid_client import client
from .models import Transaction, UserProfile  # <-- make sure you import UserProfile

# Plaid imports
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions

import datetime
from decimal import Decimal

def create_link_token(request):
    """Create a link_token to start Plaid Link"""
    user = LinkTokenCreateRequestUser(client_user_id=str(request.user.id))

    request_data = LinkTokenCreateRequest(
        products=[Products('transactions')],
        client_name='FinDice',
        country_codes=[CountryCode('US')],
        language='en',
        user=user
    )

    response = client.link_token_create(request_data)
    link_token = response['link_token']

    return JsonResponse({'link_token': link_token})

# core/views.py

@csrf_exempt
def exchange_public_token(request):
    """Exchange public_token for access_token after successful Link, then immediately fetch transactions"""

    data = json.loads(request.body)
    public_token = data['public_token']

    request_data = ItemPublicTokenExchangeRequest(public_token=public_token)
    response = client.item_public_token_exchange(request_data)

    access_token = response['access_token']
    item_id = response['item_id']

    # Save into user profile
    profile = UserProfile.objects.get(user=request.user)
    profile.bank_access_token = access_token
    profile.save()

    # Immediately fetch transactions after linking
    fetch_transactions_logic(request.user)

    return JsonResponse({'status': 'success'})



def fetch_transactions_logic(user):
    """Internal helper to fetch and save transactions for a given user"""

    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        return

    access_token = profile.bank_access_token
    if not access_token:
        return

    end_date = datetime.datetime.now().date()
    start_date = end_date - datetime.timedelta(days=90)

    request_data = TransactionsGetRequest(
        access_token=access_token,
        start_date=start_date,
        end_date=end_date,
        options=TransactionsGetRequestOptions(count=100, offset=0)
    )

    response = client.transactions_get(request_data)
    transactions = response['transactions']

    for txn in transactions:
        plaid_category = txn['category'][0].lower() if txn['category'] else 'other'
        if plaid_category not in ['food', 'rent', 'entertainment']:
            plaid_category = 'other'

        txn_type = 'expense' if txn['amount'] > 0 else 'income'

        Transaction.objects.create(
            user=user,
            amount=Decimal(str(abs(txn['amount']))),
            type=txn_type,
            category=plaid_category,
            description=txn['name'],
            date=txn['date'],
        )


@csrf_exempt
def fetch_transactions(request):
    """Public Django view to manually trigger fetching transactions if needed"""
    fetch_transactions_logic(request.user)
    return JsonResponse({'status': 'transactions fetch triggered'})

# core/views.py
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect


# core/views.py

from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.contrib import messages

@csrf_exempt
def reset_password_email(request):
    """Step 1: Ask for user's email"""

    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # Store the user ID in session temporarily
            request.session['reset_user_id'] = user.id
            return redirect('set_new_password')
        except User.DoesNotExist:
            messages.error(request, 'No account found with that email.')

    return render(request, 'reset_password_email.html')

# core/views.py

@csrf_exempt
def set_new_password(request):
    """Step 2: Set new password after email is verified"""

    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect('reset_password_email')

    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            # Clear the session
            del request.session['reset_user_id']
            messages.success(request, 'Your password has been reset successfully.')
            return redirect('login')
    else:
        form = SetPasswordForm(user)

    return render(request, 'set_new_password.html', {'form': form})




# core/views.py

@login_required
def password_reset_success(request):
    """Password changed successfully"""
    return render(request, 'password_reset_success.html')
