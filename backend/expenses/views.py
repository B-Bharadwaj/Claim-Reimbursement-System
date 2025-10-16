from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Expense
from .serializers import ExpenseSerializer
from .permissions import IsEmployeeOrReadOnly
from django.contrib.auth import get_user_model

def user_role(user):
    # relies on your CustomUser.role values: EMPLOYEE / MANAGER / FINANCE
    return getattr(user, "role", None)

@method_decorator(csrf_exempt, name='dispatch')
class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all().order_by("-created_at")
    serializer_class = ExpenseSerializer
    permission_classes = []

    #def get_permissions(self):
    # Bypass object-level owner check for workflow actions
  #      workflow_actions = [
   #         "submit", "manager_approve", "manager_reject", "finance_approve", "mark_paid"
    #    ]
     #   if getattr(self, "action", None) in workflow_actions:
      #      return [IsAuthenticated()]
    # For standard create/update/delete, enforce owner rule
       # from .permissions import IsEmployeeOrReadOnly
        #return [IsAuthenticated(), IsEmployeeOrReadOnly()]

    def get_queryset(self):
        r = user_role(self.request.user)
        base = Expense.objects.all().order_by("-created_at")

    # For detail + workflow actions, use full queryset so the object can be found.
        unrestricted_actions = {"retrieve", "submit", "manager_approve", "manager_reject", "finance_approve", "mark_paid"}
        if getattr(self, "action", None) in unrestricted_actions:
            return base

    # For LIST view, filter by role (so each role sees the right queue)
        if r == "EMPLOYEE":
            return base.filter(submitted_by=self.request.user)
        elif r == "MANAGER":
            return base.filter(Q(status=Expense.Status.SUBMITTED) | Q(submitted_by=self.request.user))
        elif r == "FINANCE":
            return base.filter(Q(status=Expense.Status.MANAGER_APPROVED) | Q(submitted_by=self.request.user))
        return Expense.objects.none()


    def perform_create(self, serializer):
        User = get_user_model()
        default_user = User.objects.first()  # pick the first existing user
        serializer.save(submitted_by=default_user)

    # ----- Workflow actions -----

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        exp = self.get_object()
        if exp.submitted_by != request.user:
            return Response({"detail": "Not your expense."}, status=403)
        if exp.status not in [Expense.Status.DRAFT]:
            return Response({"detail": "Only draft can be submitted."}, status=400)
        exp.status = Expense.Status.SUBMITTED
        exp.save()
        return Response(ExpenseSerializer(exp).data)

    @action(detail=True, methods=["post"])
    def manager_approve(self, request, pk=None):
        if user_role(request.user) != "MANAGER":
            return Response({"detail": "Manager role required."}, status=403)
        exp = self.get_object()
        if not exp.can_approve_by_manager():
            return Response({"detail": "Not eligible for manager approval."}, status=400)
        exp.status = Expense.Status.MANAGER_APPROVED
        exp.manager = request.user
        exp.save()
        return Response(ExpenseSerializer(exp).data)

    @action(detail=True, methods=["post"])
    def manager_reject(self, request, pk=None):
        if user_role(request.user) != "MANAGER":
            return Response({"detail": "Manager role required."}, status=403)
        exp = self.get_object()
        if not exp.can_approve_by_manager():
            return Response({"detail": "Not eligible for manager rejection."}, status=400)
        exp.status = Expense.Status.MANAGER_REJECTED
        exp.manager = request.user
        exp.save()
        return Response(ExpenseSerializer(exp).data)

    @action(detail=True, methods=["post"])
    def finance_approve(self, request, pk=None):
        if user_role(request.user) != "FINANCE":
            return Response({"detail": "Finance role required."}, status=403)
        exp = self.get_object()
        if not exp.can_approve_by_finance():
            return Response({"detail": "Not eligible for finance approval."}, status=400)
        exp.status = Expense.Status.FINANCE_APPROVED
        exp.finance_reviewer = request.user
        exp.save()
        return Response(ExpenseSerializer(exp).data)

    @action(detail=True, methods=["post"])
    def mark_paid(self, request, pk=None):
        if user_role(request.user) != "FINANCE":
            return Response({"detail": "Finance role required."}, status=403)
        exp = self.get_object()
        if exp.status != Expense.Status.FINANCE_APPROVED:
            return Response({"detail": "Only finance-approved expenses can be marked Paid."}, status=400)
        exp.status = Expense.Status.PAID
        exp.save()
        return Response(ExpenseSerializer(exp).data)
