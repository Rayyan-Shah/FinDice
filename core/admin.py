from django.contrib.auth.models import User

from .models import Transaction
from django.contrib import admin


admin.site.register(Transaction)

