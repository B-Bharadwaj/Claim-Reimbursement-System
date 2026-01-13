from rest_framework import serializers
from .models import Expense

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = [
            "id",
            "title",
            "amount",
            "category",
            "description",
            "receipt",
            "status",

            "submitted_by",
            "manager_comment",
            "approved_by",

            "finance_comment",
            "paid_by",
            "payment_reference",

            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "submitted_by",
            "approved_by",
            "paid_by",
            "created_at",
            "updated_at",
        ]
