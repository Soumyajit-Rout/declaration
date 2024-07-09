from rest_framework.permissions import BasePermission
from rest_framework.request import Request



STATIC_API_TOKEN = "12345"
def is_authenticated(request: Request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return False
    token = auth_header.split(' ')[1]
    if token != STATIC_API_TOKEN:
        return False
    return True

class StaticTokenPermission(BasePermission):
    def has_permission(self, request, view):
        return is_authenticated(request)