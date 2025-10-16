from django.db import models
from django.conf import settings

class Expense(models.Model):
    class Category(models.TextChoices):
        TRAVEL = "TRAVEL", "Travel"
        FOOD = "FOOD", "Food"
        SUPPLIES = "SUPPLIES", "Office Supplies"
        SOFTWARE = "SOFTWARE", "Software"
        OTHER = "OTHER", "Other"

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMITTED = "SUBMITTED", "Submitted"
        MANAGER_APPROVED = "MANAGER_APPROVED", "Manager Approved"
        MANAGER_REJECTED = "MANAGER_REJECTED", "Manager Rejected"
        FINANCE_APPROVED = "FINANCE_APPROVED", "Finance Approved"
        PAID = "PAID", "Paid"

    title = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    description = models.TextField(blank=True)
    receipt = models.FileField(upload_to="receipts/", blank=True, null=True)

    # Who submitted and who acted
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="expenses")
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="manager_expenses")
    finance_reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="finance_expenses")

    status = models.CharField(max_length=30, choices=Status.choices, default=Status.DRAFT)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def can_approve_by_manager(self):
        return self.status in [self.Status.SUBMITTED]

    def can_approve_by_finance(self):
        return self.status == self.Status.MANAGER_APPROVED

    def __str__(self):
        return f"{self.title} - {self.amount} ({self.status})"
