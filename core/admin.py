from django.contrib import admin
from .models import Transaction, UserProfile, Budget, FinancialGoal, APIConfig, SystemPrompt

# Register your models here
admin.site.register(Transaction)
admin.site.register(UserProfile)
admin.site.register(Budget)
admin.site.register(FinancialGoal)
admin.site.register(APIConfig)
admin.site.register(SystemPrompt)

