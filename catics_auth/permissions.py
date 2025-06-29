from rest_framework import permissions
from .models import Validation

class IsValidated(permissions.BasePermission):
    """
    User email address has to be validated
    """

    message = 'Veuillez valider votre adresse email'
    code = 'unvalidated'

    def has_permission(self, request, view):
        return Validation.objects.filter(user=request.user, is_validated=True).exists()
