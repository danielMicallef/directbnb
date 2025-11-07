from rest_framework import permissions


class IsLeadRegistrationNotCompleted(permissions.BasePermission):
    """
    Allows access only if the related lead registration is not completed.
    """

    def has_object_permission(self, request, view, obj):
        return obj.lead_registration.completed_at is None
