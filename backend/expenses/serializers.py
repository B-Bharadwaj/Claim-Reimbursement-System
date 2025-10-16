from rest_framework import serializers
from .models import Expense

class ExpenseSerializer(serializers.ModelSerializer):
    submitted_by_username = serializers.ReadOnlyField(source="submitted_by.username")

    class Meta:
        model = Expense
        fields = [
            "id", "title", "amount", "category", "description", "receipt",
            "submitted_by", "submitted_by_username", "manager", "finance_reviewer",
            "status", "created_at", "updated_at"
        ]
        read_only_fields = ["submitted_by", "manager", "finance_reviewer", "status", "created_at", "updated_at"]
