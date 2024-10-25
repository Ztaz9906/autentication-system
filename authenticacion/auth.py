from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from rest_framework import exceptions


class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user_model = get_user_model()
        try:
            user = user_model.objects.get(Q(email=username) | Q(username=username))
        except user_model.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                if not user.is_active:
                    raise exceptions.PermissionDenied("Esta cuenta no está activa.")
                return user
        return None