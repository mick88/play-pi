from django.conf import settings
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import BasePermission, SAFE_METHODS


class ApiPermission(BasePermission):
    def has_permission(self, request, view):
        # logged in user always has access
        if request.user.is_authenticated:
            return True

        # If login is requried, no anonymous access
        if settings.LOGIN_REQUIRED:
            return False

        # If login is required to control playback, only safe methods are required
        if settings.PLAYBACK_CONTROL_LOGIN_REQUIRED and request.method not in SAFE_METHODS:
            return False

        # User is not authenticated, but login is not required
        return True


class SessionAuthenticationNoCsrf(SessionAuthentication):
    """
    Session authentication without csrf
    """
    def enforce_csrf(self, request):
        pass