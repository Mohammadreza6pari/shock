from rest_framework.permissions import BasePermission

class IsApprovedUser(BasePermission):
    """
    Allows access only to approved users.
    """
    message = "Your account is not approved by admin yet."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "is_approved", False)
        )