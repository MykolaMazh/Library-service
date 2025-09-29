from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsBorrower(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return (
            request.method in SAFE_METHODS or request.user.is_staff
        ) or request.method == "POST"

    def has_object_permission(self, request, view, obj):
        return (obj.user == request.user) or (request.user.is_staff)
