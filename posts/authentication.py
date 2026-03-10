from django.contrib.auth.models import User
from rest_framework import authentication, exceptions
from firebase_admin import auth

class FirebaseAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None

        id_token = auth_header.split(' ').pop()
        
        try:
            decoded_token = auth.verify_id_token(id_token)
        except Exception:
            raise exceptions.AuthenticationFailed('Invalid Firebase ID Token')

        uid = decoded_token.get('uid')
        email = decoded_token.get('email')
        name = decoded_token.get('name', '')

        if not uid:
            raise exceptions.AuthenticationFailed('Firebase UID not found in token')

        user, created = User.objects.get_or_create(username=uid)
        
        if created:
            user.email = email
            user.first_name = name
            user.save()

        return (user, None)
