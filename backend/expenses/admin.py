from django.contrib import admin
from .models import Expense

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "amount", "category", "status", "submitted_by", "created_at")
    list_filter = ("status", "category", "created_at")
    search_fields = ("title", "description", "submitted_by__username")
