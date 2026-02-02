from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status as drf_status

from django.http import FileResponse, Http404
from django.utils.encoding import smart_str

from rest_framework.exceptions import PermissionDenied

from .models import Expense, Receipt, ApprovalHistory
from .serializers import ExpenseSerializer, ReceiptUploadSerializer


def user_role(user):
    # relies on your CustomUser.role values: EMPLOYEE / MANAGER / FINANCE
    return getattr(user, "role", None)


def can_view_receipt(user, exp: Expense) -> bool:
    role = user_role(user)

    if role == "EMPLOYEE":
        return exp.submitted_by_id == user.id

    if role == "MANAGER":
        # Manager can view receipts once submitted onwards
        return exp.status in [
            Expense.Status.SUBMITTED,
            Expense.Status.APPROVED,
            Expense.Status.REJECTED,
            Expense.Status.FINANCE_APPROVED,
            Expense.Status.PAID,
        ]

    if role == "FINANCE":
        return exp.status in [
            Expense.Status.APPROVED,
            Expense.Status.FINANCE_APPROVED,
            Expense.Status.PAID,
        ]

    return False


class ReceiptViewSet(viewsets.ModelViewSet):
    serializer_class = ReceiptUploadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        role = user_role(self.request.user)
        qs = Receipt.objects.select_related("expense").all().order_by("-id")

        if role == "EMPLOYEE":
            return qs.filter(expense__submitted_by=self.request.user)

        if role == "MANAGER":
            return qs.filter(expense__status__in=[
                Expense.Status.SUBMITTED,
                Expense.Status.APPROVED,
                Expense.Status.REJECTED,
                Expense.Status.FINANCE_APPROVED,
                Expense.Status.PAID,
            ])

        if role == "FINANCE":
            return qs.filter(expense__status__in=[
                Expense.Status.APPROVED,
                Expense.Status.FINANCE_APPROVED,
                Expense.Status.PAID,
            ])

        return Receipt.objects.none()

    def perform_create(self, serializer):
        exp = serializer.validated_data["expense"]
        if exp.submitted_by_id != self.request.user.id:
            raise PermissionDenied("Not allowed to upload to this claim.")
        serializer.save()


class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]
    queryset = Expense.objects.all().order_by("-created_at")

    def get_queryset(self):
        role = user_role(self.request.user)
        base = super().get_queryset()

        unrestricted_actions = {"submit", "manager_approve", "manager_reject", "finance_approve", "mark_paid", "receipt"}
        if getattr(self, "action", None) in unrestricted_actions:
            return base

        # list view queues
        if role == "EMPLOYEE":
            return base.filter(submitted_by=self.request.user)

        if role == "MANAGER":
            return base.filter(status=Expense.Status.SUBMITTED, current_approver=self.request.user)

        if role == "FINANCE":
            return base.filter(status=Expense.Status.APPROVED)

        return Expense.objects.none()

    def perform_create(self, serializer):
        # ✅ Any role can create → DRAFT
        serializer.save(
            submitted_by=self.request.user,
            status=Expense.Status.DRAFT,
            current_approver=None,
        )

    # ---- Workflow actions ----

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        exp = self.get_object()

        if exp.submitted_by_id != request.user.id:
            return Response({"detail": "Not your claim."}, status=drf_status.HTTP_403_FORBIDDEN)

        if exp.status != Expense.Status.DRAFT:
            return Response({"detail": "Only draft can be submitted."}, status=drf_status.HTTP_400_BAD_REQUEST)

        manager = getattr(request.user, "reports_to", None)
        if not manager:
            return Response({"detail": "No manager assigned (reports_to)."}, status=drf_status.HTTP_400_BAD_REQUEST)

        if manager.id == request.user.id:
            return Response({"detail": "Self-approval is not allowed."}, status=drf_status.HTTP_400_BAD_REQUEST)

        exp.status = Expense.Status.SUBMITTED
        exp.current_approver = manager
        exp.save(update_fields=["status", "current_approver", "updated_at"])

        ApprovalHistory.objects.create(
            expense=exp,
            approver=request.user,
            action=ApprovalHistory.Action.SUBMITTED,
            remarks="Submitted",
        )

        return Response(ExpenseSerializer(exp, context={"request": request}).data)

    @action(detail=True, methods=["post"])
    def manager_approve(self, request, pk=None):
        exp = self.get_object()

        if exp.current_approver_id != request.user.id:
            return Response({"detail": "You are not the current approver."}, status=drf_status.HTTP_403_FORBIDDEN)

        if exp.submitted_by_id == request.user.id:
            return Response({"detail": "Self-approval is not allowed."}, status=drf_status.HTTP_400_BAD_REQUEST)

        if exp.status != Expense.Status.SUBMITTED:
            return Response({"detail": "Not eligible for approval."}, status=drf_status.HTTP_400_BAD_REQUEST)

        exp.status = Expense.Status.APPROVED
        exp.approved_by = request.user
        exp.manager_comment = request.data.get("manager_comment", "")
        exp.current_approver = None
        exp.save(update_fields=["status", "approved_by", "manager_comment", "current_approver", "updated_at"])

        ApprovalHistory.objects.create(
            expense=exp,
            approver=request.user,
            action=ApprovalHistory.Action.APPROVED,
            remarks=exp.manager_comment,
        )

        return Response(ExpenseSerializer(exp, context={"request": request}).data)

    @action(detail=True, methods=["post"])
    def manager_reject(self, request, pk=None):
        exp = self.get_object()

        if exp.current_approver_id != request.user.id:
            return Response({"detail": "You are not the current approver."}, status=drf_status.HTTP_403_FORBIDDEN)

        if exp.submitted_by_id == request.user.id:
            return Response({"detail": "Self-approval is not allowed."}, status=drf_status.HTTP_400_BAD_REQUEST)

        if exp.status != Expense.Status.SUBMITTED:
            return Response({"detail": "Not eligible for rejection."}, status=drf_status.HTTP_400_BAD_REQUEST)

        exp.status = Expense.Status.REJECTED
        exp.approved_by = request.user
        exp.manager_comment = request.data.get("manager_comment", "")
        exp.current_approver = None
        exp.save(update_fields=["status", "approved_by", "manager_comment", "current_approver", "updated_at"])

        ApprovalHistory.objects.create(
            expense=exp,
            approver=request.user,
            action=ApprovalHistory.Action.REJECTED,
            remarks=exp.manager_comment,
        )

        return Response(ExpenseSerializer(exp, context={"request": request}).data)

    @action(detail=True, methods=["post"])
    def finance_approve(self, request, pk=None):
        if user_role(request.user) != "FINANCE":
            return Response({"detail": "Finance role required."}, status=drf_status.HTTP_403_FORBIDDEN)

        exp = self.get_object()
        if exp.status != Expense.Status.APPROVED:
            return Response({"detail": "Not eligible for finance approval."}, status=drf_status.HTTP_400_BAD_REQUEST)

        exp.status = Expense.Status.FINANCE_APPROVED
        exp.finance_comment = request.data.get("finance_comment", "")
        exp.save(update_fields=["status", "finance_comment", "updated_at"])

        ApprovalHistory.objects.create(
            expense=exp,
            approver=request.user,
            action=ApprovalHistory.Action.FINANCE_APPROVED,
            remarks=exp.finance_comment,
        )

        return Response(ExpenseSerializer(exp, context={"request": request}).data)

    @action(detail=True, methods=["post"])
    def mark_paid(self, request, pk=None):
        if user_role(request.user) != "FINANCE":
            return Response({"detail": "Finance role required."}, status=drf_status.HTTP_403_FORBIDDEN)

        exp = self.get_object()
        if exp.status != Expense.Status.FINANCE_APPROVED:
            return Response({"detail": "Only finance-approved claims can be marked Paid."}, status=drf_status.HTTP_400_BAD_REQUEST)

        exp.status = Expense.Status.PAID
        exp.paid_by = request.user
        exp.payment_reference = request.data.get("payment_reference", "")
        exp.finance_comment = request.data.get("finance_comment", exp.finance_comment)
        exp.save(update_fields=["status", "paid_by", "payment_reference", "finance_comment", "updated_at"])

        ApprovalHistory.objects.create(
            expense=exp,
            approver=request.user,
            action=ApprovalHistory.Action.PAID,
            remarks=f"Ref: {exp.payment_reference}".strip(),
        )

        return Response(ExpenseSerializer(exp, context={"request": request}).data)

    @action(detail=True, methods=["get"], url_path="receipt")
    def receipt(self, request, pk=None):
        exp = self.get_object()

        if not can_view_receipt(request.user, exp):
            return Response({"detail": "Not allowed."}, status=drf_status.HTTP_403_FORBIDDEN)

        receipt_obj = exp.receipts.order_by("-id").first()

        file_field = None
        if receipt_obj and receipt_obj.file:
            file_field = receipt_obj.file
        elif getattr(exp, "receipt", None):
            file_field = exp.receipt

        if not file_field:
            raise Http404("No receipt found")

        download = request.query_params.get("download") == "1"
        f = file_field.open("rb")
        filename = smart_str(file_field.name.split("/")[-1])

        return FileResponse(f, as_attachment=download, filename=filename)
