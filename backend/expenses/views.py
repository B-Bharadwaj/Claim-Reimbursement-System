from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status as drf_status

from .models import Expense
from .serializers import ExpenseSerializer


def user_role(user):
    # relies on your CustomUser.role values: EMPLOYEE / MANAGER / FINANCE
    return getattr(user, "role", None)


class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]
    queryset = Expense.objects.all().order_by("-created_at")

    def get_queryset(self):
        role = user_role(self.request.user)
        base = super().get_queryset()

        # detail + workflow actions can access object (but role checks still apply)
        unrestricted_actions = {"retrieve", "submit", "manager_approve", "manager_reject", "finance_approve", "mark_paid"}
        if getattr(self, "action", None) in unrestricted_actions:
            return base

        # list view queues
        if role == "EMPLOYEE":
            return base.filter(submitted_by=self.request.user)

        if role == "MANAGER":
            return base.filter(status=Expense.Status.SUBMITTED)

        if role == "FINANCE":
            return base.filter(status=Expense.Status.MANAGER_APPROVED)

        return Expense.objects.none()

    def perform_create(self, serializer):
        # employee creates -> becomes submitted by default
        serializer.save(
            submitted_by=self.request.user,
            status=Expense.Status.SUBMITTED
        )

    # ---- Workflow actions ----

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        exp = self.get_object()
        if exp.submitted_by != request.user:
            return Response({"detail": "Not your claim."}, status=drf_status.HTTP_403_FORBIDDEN)
        if exp.status != Expense.Status.DRAFT:
            return Response({"detail": "Only draft can be submitted."}, status=drf_status.HTTP_400_BAD_REQUEST)

        exp.status = Expense.Status.SUBMITTED
        exp.save()
        return Response(ExpenseSerializer(exp, context={"request": request}).data)

    @action(detail=True, methods=["post"])
    def manager_approve(self, request, pk=None):
        if user_role(request.user) != "MANAGER":
            return Response({"detail": "Manager role required."}, status=drf_status.HTTP_403_FORBIDDEN)

        exp = self.get_object()
        if not exp.can_approve_by_manager():
            return Response({"detail": "Not eligible for manager approval."}, status=drf_status.HTTP_400_BAD_REQUEST)

        exp.status = Expense.Status.MANAGER_APPROVED
        exp.approved_by = request.user
        exp.manager_comment = request.data.get("manager_comment", "")
        exp.save()
        return Response(ExpenseSerializer(exp, context={"request": request}).data)

    @action(detail=True, methods=["post"])
    def manager_reject(self, request, pk=None):
        if user_role(request.user) != "MANAGER":
            return Response({"detail": "Manager role required."}, status=drf_status.HTTP_403_FORBIDDEN)

        exp = self.get_object()
        if not exp.can_approve_by_manager():
            return Response({"detail": "Not eligible for manager rejection."}, status=drf_status.HTTP_400_BAD_REQUEST)

        exp.status = Expense.Status.MANAGER_REJECTED
        exp.approved_by = request.user
        exp.manager_comment = request.data.get("manager_comment", "")
        exp.save()
        return Response(ExpenseSerializer(exp, context={"request": request}).data)

    @action(detail=True, methods=["post"])
    def finance_approve(self, request, pk=None):
        if user_role(request.user) != "FINANCE":
            return Response({"detail": "Finance role required."}, status=drf_status.HTTP_403_FORBIDDEN)

        exp = self.get_object()
        if not exp.can_approve_by_finance():
            return Response({"detail": "Not eligible for finance approval."}, status=drf_status.HTTP_400_BAD_REQUEST)

        exp.status = Expense.Status.FINANCE_APPROVED
        exp.finance_comment = request.data.get("finance_comment", "")
        exp.save()
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
        exp.finance_comment = request.data.get("finance_comment", "")
        exp.save()
        return Response(ExpenseSerializer(exp, context={"request": request}).data)
