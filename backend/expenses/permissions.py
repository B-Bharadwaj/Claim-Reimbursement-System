from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsEmployeeOrReadOnly(BasePermission):
    """
    Employees can create/update only their own expenses.
    Managers/Finance can read; actions controlled in view actions.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        # employees can modify only their own drafts/submitted
        return obj.submitted_by_id == request.user.id
