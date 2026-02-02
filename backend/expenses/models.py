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
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        FINANCE_APPROVED = "FINANCE_APPROVED", "Finance Approved"
        PAID = "PAID", "Paid"

    title = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    description = models.TextField(blank=True)

    current_approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="claims_to_approve",
    )

    # Optional legacy field (you already use Receipt model too)
    receipt = models.FileField(upload_to="receipts/", blank=True, null=True)

    status = models.CharField(max_length=30, choices=Status.choices, default=Status.DRAFT)

    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="claims_submitted",
    )

    manager_comment = models.TextField(blank=True, default="")
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="claims_approved",
    )

    finance_comment = models.TextField(blank=True, default="")
    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="claims_paid",
    )

    payment_reference = models.CharField(max_length=100, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def can_approve_by_manager(self):
        return self.status == self.Status.SUBMITTED

    def can_approve_by_finance(self):
        return self.status == self.Status.APPROVED

    def __str__(self):
        return f"{self.title} - {self.amount} ({self.status})"


class Receipt(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name="receipts")
    file = models.FileField(upload_to="receipts/")

    OCR_STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    ]
    ocr_status = models.CharField(max_length=10, choices=OCR_STATUS_CHOICES, default="PENDING")
    ocr_confidence = models.FloatField(null=True, blank=True)
    ocr_result = models.JSONField(null=True, blank=True)
    ocr_error = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Receipt({self.id}) for Expense({self.expense_id})"


class ApprovalHistory(models.Model):
    class Action(models.TextChoices):
        SUBMITTED = "SUBMITTED", "Submitted"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        FINANCE_APPROVED = "FINANCE_APPROVED", "Finance Approved"
        PAID = "PAID", "Paid"

    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name="approval_history")
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    action = models.CharField(max_length=30, choices=Action.choices)
    remarks = models.TextField(blank=True, default="")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.expense_id} - {self.action}"
