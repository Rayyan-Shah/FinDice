from .models import Transaction
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Budget, FinancialGoal
from django import forms
from datetime import datetime


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'type', 'category', 'description']

    def __init__(self, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)
        self.fields['category'].required = False
        self.fields['category'].widget.attrs.update({'id': 'id_category'})

    def clean(self):
        cleaned_data = super().clean()
        trans_type = cleaned_data.get('type')
        category = cleaned_data.get('category')

        if trans_type == 'expense':
            if not category:
                self.add_error('category', 'Category is required for expenses.')
        else:
            cleaned_data['category'] = None  # Explicitly set no category for cash/income

        return cleaned_data


class BudgetForm(forms.ModelForm):
    month = forms.CharField(widget=forms.TextInput(attrs={'type': 'month'}))

    class Meta:
        model = Budget
        fields = ['month', 'amount']

    def clean_month(self):
        raw_month = self.cleaned_data['month']
        try:
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


class FinancialGoalForm(forms.ModelForm):
    class Meta:
        model = FinancialGoal
        fields = ['target_amount']
        widgets = {
            'target_amount': forms.NumberInput(attrs={'placeholder': 'Enter target amount'})
        }


class AddToSavingsForm(forms.ModelForm):
    class Meta:
        model = FinancialGoal
        fields = ['current_savings']
        widgets = {
            'current_savings': forms.NumberInput(attrs={'placeholder': 'Enter amount to add to savings'})
        }


class AccountSettingsForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    income = forms.DecimalField(max_digits=10, decimal_places=2, required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(AccountSettingsForm, self).__init__(*args, **kwargs)
        if user:
            profile, created = UserProfile.objects.get_or_create(user=user)
            self.fields['income'].initial = profile.income

    def save(self, commit=True):
        user = super(AccountSettingsForm, self).save(commit)
        income = self.cleaned_data['income']
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.income = income
        if commit:
            profile.save()
        return user
