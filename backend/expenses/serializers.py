from rest_framework import serializers
from django.conf import settings
from .models import Expense, Receipt
from .services.ocr_client import call_ocr_service, OCRServiceError

class ExpenseSerializer(serializers.ModelSerializer):
    has_receipt = serializers.SerializerMethodField()
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
            "has_receipt",
        ]
        read_only_fields = [
            "submitted_by",
            "approved_by",
            "paid_by",
            "created_at",
            "updated_at",
            "has_receipt",
        ]

    def get_has_receipt(self, obj):
        # supports both old Expense.receipt and Receipt model
        if getattr(obj, "receipt", None):
            return True
        return obj.receipts.exists()

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
