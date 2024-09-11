# File contaning all the utility functions
from django.conf import settings
from urllib.request import Request


#To-Do Change it to dynamic as soon as auth functionality is decided
class Authentication:

    @staticmethod
    def is_authenticated(request: Request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return False
        token = auth_header.split(' ')[1]
        if token != settings.STATIC_API_TOKEN:
            return False
        return True
