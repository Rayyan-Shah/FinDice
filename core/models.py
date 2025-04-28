from django.db import models
from django.contrib.auth.models import User

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('cash', 'Cash'),
    ]

    CATEGORY_CHOICES = [
        ('food', 'Food'),
        ('rent', 'Rent'),
        ('entertainment', 'Entertainment'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        blank=True,
        null=True
    )
    description = models.TextField(blank=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - ${self.amount} on {self.date}"


class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    income = models.DecimalField(max_digits=10, decimal_places=2)
    bank_access_token = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username


class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.username} - {self.month.strftime('%B %Y')} Budget"


class FinancialGoal(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_savings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_progress_percentage(self):
        if self.target_amount == 0:
            return 0
        return (self.current_savings / self.target_amount) * 100

    def __str__(self):
        return f"Goal for {self.user.username}: ${self.target_amount} - Saved: ${self.current_savings}"


class APIConfig(models.Model):
    service_name = models.CharField(max_length=100, default='SAMBANOVA')
    api_key = models.CharField(max_length=255)

    def __str__(self):
        return f"API Key for {self.service_name}"


class PlaidConfig(models.Model):
    client_id = models.CharField(max_length=255)
    secret = models.CharField(max_length=255)
    environment = models.CharField(max_length=50, choices=[
        ('sandbox', 'Sandbox'),
        ('development', 'Development'),
        ('production', 'Production'),
    ])

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Plaid Config ({self.environment})"



class SystemPrompt(models.Model):
    name = models.CharField(max_length=100)
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

