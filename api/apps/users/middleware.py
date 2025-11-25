from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth.models import AnonymousUser
from apps.users.models import User

class SimpleJWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                UntypedToken(token)
                
                from rest_framework_simplejwt.tokens import AccessToken
                access_token = AccessToken(token)
                user_id = access_token.get('user_id')
                
                if user_id:
                    try:
                        user = User.objects.get(id=user_id, status='Active')
                        class AuthenticatedUser:
                            def __init__(self, artemis_user):
                                self.id = artemis_user.id
                                self.email = artemis_user.email
                                self.name = artemis_user.name
                                self.role = artemis_user.role
                                self.status = artemis_user.status
                                self.is_authenticated = True
                                self.is_active = artemis_user.status == 'Active'
                            
                            def get(self, key):
                                return getattr(self, key, None)
                        
                        request.user = AuthenticatedUser(user)
                    except User.DoesNotExist:
                        request.user = AnonymousUser()
                else:
                    request.user = AnonymousUser()
                    
            except (InvalidToken, TokenError):
                request.user = AnonymousUser()
        else:
            request.user = AnonymousUser()

        response = self.get_response(request)
        return response