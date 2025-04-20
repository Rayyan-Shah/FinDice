from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
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
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    date = models.DateField(auto_now_add=True)
    def __str__(self):
        return f"{self.type} - ${self.amount} on {self.date}"


from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    income = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return self.user.username

from django.db import models
from django.contrib.auth.models import User

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.DateField()  # Just use the 1st of the month to mark the month
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.username} - {self.month.strftime('%B %Y')} Budget"



class FinancialTip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tip = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=100, blank=True, null=True)  # You can categorize tips if needed

    def __str__(self):
        return f"Tip for {self.user.username}: {self.tip[:30]}..."
