from rest_framework import serializers
from django.conf import settings
from .models import Expense, Receipt, ApprovalHistory
from .services.ocr_client import call_ocr_service, OCRServiceError


class ApprovalHistorySerializer(serializers.ModelSerializer):
    approver_username = serializers.SerializerMethodField()

    class Meta:
        model = ApprovalHistory
        fields = [
            "id",
            "action",
            "remarks",
            "timestamp",
            "approver",
            "approver_username",
        ]
        read_only_fields = fields

    def get_approver_username(self, obj):
        if obj.approver:
            return obj.approver.username
        return None


class ExpenseSerializer(serializers.ModelSerializer):
    has_receipt = serializers.SerializerMethodField()

    # ✅ NEW: approval history included in claim detail response
    approval_history = ApprovalHistorySerializer(many=True, read_only=True)

    # ✅ NEW: helpful display for UI
    submitted_by_username = serializers.SerializerMethodField()
    current_approver_username = serializers.SerializerMethodField()

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
            "submitted_by_username",

            # ✅ NEW: routing field
            "current_approver",
            "current_approver_username",

            "manager_comment",
            "approved_by",

            "finance_comment",
            "paid_by",
            "payment_reference",

            "created_at",
            "updated_at",
            "has_receipt",

            # ✅ NEW: audit trail
            "approval_history",
        ]
        read_only_fields = [
            "submitted_by",
            "submitted_by_username",
            "current_approver",
            "current_approver_username",
            "approved_by",
            "paid_by",
            "created_at",
            "updated_at",
            "has_receipt",
            "approval_history",
        ]

    def get_has_receipt(self, obj):
        # supports both old Expense.receipt and Receipt model
        if getattr(obj, "receipt", None):
            return True
        return obj.receipts.exists()

    def get_submitted_by_username(self, obj):
        return obj.submitted_by.username if obj.submitted_by else None

    def get_current_approver_username(self, obj):
        return obj.current_approver.username if getattr(obj, "current_approver", None) else None


class ReceiptUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = ["id", "expense", "file", "ocr_status", "ocr_confidence", "ocr_result", "ocr_error"]
        read_only_fields = ["ocr_status", "ocr_confidence", "ocr_result", "ocr_error"]

    def create(self, validated_data):
        receipt = super().create(validated_data)

        # default
        receipt.ocr_status = "PENDING"
        receipt.save(update_fields=["ocr_status"])

        try:
            ocr_json = call_ocr_service(
                base_url=settings.OCR_SERVICE_URL,
                file_path=receipt.file.path,
                timeout_seconds=settings.OCR_TIMEOUT_SECONDS,
            )
            receipt.ocr_status = "SUCCESS"
            receipt.ocr_result = ocr_json
            receipt.ocr_confidence = ocr_json.get("confidence")
            receipt.ocr_error = None
            receipt.save(update_fields=["ocr_status", "ocr_result", "ocr_confidence", "ocr_error"])
        except OCRServiceError as e:
            receipt.ocr_status = "FAILED"
            receipt.ocr_error = str(e)
            receipt.save(update_fields=["ocr_status", "ocr_error"])

        return receipt
