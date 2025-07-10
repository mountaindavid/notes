import time
import jwt
from django.conf import settings
from rest_framework import permissions
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


class JWTAuthentication(permissions.BasePermission):
    def has_permission(self, request, view):
        token = request.headers.get('Authorization')
        if not token:
            return False
        
        try:
            token = token.split(' ')[1]
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            current_time = int(time.time())
            if current_time > payload['exp']:
                return False

            user = User.objects.get(id=payload['user_id'])
            request.user = user
            return True
        except (jwt.InvalidTokenError, ObjectDoesNotExist, IndexError): 
            return False
        





        