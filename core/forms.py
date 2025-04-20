from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Transaction

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'type', 'category', 'description']

# forms.py
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import UserProfile

from django import forms
from .models import Budget
# forms.py
# forms.py
from django import forms
from .models import Budget
from datetime import datetime

class BudgetForm(forms.ModelForm):
    month = forms.CharField(widget=forms.TextInput(attrs={'type': 'month'}))

    class Meta:
        model = Budget
        fields = ['month', 'amount']

    def clean_month(self):
        raw_month = self.cleaned_data['month']  # e.g., '2025-02'
        try:
            # Add day manually and parse into a date
            return datetime.strptime(raw_month + '-01', '%Y-%m-%d').date()
        except ValueError:
            raise forms.ValidationError("Invalid month format.")




class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    income = forms.DecimalField(max_digits=10, decimal_places=2, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'income', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit)
        income = self.cleaned_data.get('income')
        UserProfile.objects.create(user=user, income=income)
        return user

