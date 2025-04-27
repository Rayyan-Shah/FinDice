from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.db.models import Sum
from datetime import date
from .models import Transaction, Budget, FinancialGoal

def send_financial_summary_email(user):
    today = date.today()
    current_month = today.month
    current_year = today.year

    transactions = Transaction.objects.filter(
        user=user,
        date__year=current_year,
        date__month=current_month
    )

    income_total = transactions.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    expense_total = transactions.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    cash_total = transactions.filter(type='cash').aggregate(Sum('amount'))['amount__sum'] or 0

    try:
        budget = Budget.objects.get(user=user, month__year=current_year, month__month=current_month)
        budget_amount = budget.amount
    except Budget.DoesNotExist:
        budget_amount = None

    try:
        goal = FinancialGoal.objects.get(user=user)
        goal_progress = f"{goal.get_progress_percentage():.2f}%"
    except FinancialGoal.DoesNotExist:
        goal_progress = "No goal set."

    subject = "Your Monthly Financial Summary 📊"
    message = f"""
Hello {user.username},

Here’s your financial summary for {today.strftime('%B %Y')}:

- Income: ${income_total:.2f}
- Expenses: ${expense_total:.2f}
- Cash Transactions: ${cash_total:.2f}
- Budget: {'$' + str(budget_amount) if budget_amount else 'No budget set'}
- Financial Goal Progress: {goal_progress}

Keep tracking your finances and reach your goals!

- MoneyParce Team
    """

    send_mail(
        subject,
        message,
        'sciencebahlouli@gmail.com',
        [user.email],
        fail_silently=False,
    )

def send_monthly_summaries():
    users = User.objects.all()
    for user in users:
        if user.email:
            send_financial_summary_email(user)
