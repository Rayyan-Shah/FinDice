from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import TransactionForm
from .models import Transaction
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
    return render(request, 'dashboard.html')

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
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    return render(request, 'view_transactions.html', {'transactions': transactions})
