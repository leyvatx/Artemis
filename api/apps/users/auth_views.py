from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.viewsets import ViewSet
from drf_spectacular.utils import extend_schema
from .models import User
from .auth_serializers import RegisterSerializer, LoginSerializer, UserAuthSerializer
from apps.events import EventLogger


class AuthViewSet(ViewSet):
    """Authentication endpoints"""
    permission_classes = [AllowAny]
    queryset = None  # Not needed for ViewSet with custom actions
    
    @extend_schema(
        request=RegisterSerializer,
        responses={201: UserAuthSerializer},
        description="Register a new user with email and password"
    )
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """
        Register a new user.
        """
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Log the registration event
            EventLogger.log_event(
                user=user,
                title="User Registered",
                category=EventLogger.USER_CREATED,
                description=f"New user registered: {user.email}",
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            response_serializer = UserAuthSerializer(user)
            
            return Response(
                {
                    'success': True,
                    'message': 'User registered successfully',
                    'data': response_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            {
                'success': False,
                'message': 'Registration failed',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @extend_schema(
        request=LoginSerializer,
        responses={200: UserAuthSerializer},
        description="Login with email and password to receive JWT tokens"
    )
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """
        Login a user and receive JWT tokens.
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Log the login event
            EventLogger.log_login(
                user=user,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            response_serializer = UserAuthSerializer(user)
            
            return Response(
                {
                    'success': True,
                    'message': 'Login successful',
                    'data': response_serializer.data
                },
                status=status.HTTP_200_OK
            )
        
        # Log failed login attempt
        email = request.data.get('email', 'unknown')
        EventLogger.log_login_failed(
            user=None,
            reason='Invalid credentials',
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response(
            {
                'success': False,
                'message': 'Login failed',
                'errors': serializer.errors
            },
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    @extend_schema(
        request=None,
        responses={200: None},
        description="Logout current user"
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """
        Logout a user.
        """
        # Log the logout event
        EventLogger.log_logout(
            user=request.user,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response(
            {
                'success': True,
                'message': 'Logout successful'
            },
            status=status.HTTP_200_OK
        )
    
    @extend_schema(
        request=None,
        responses={200: UserAuthSerializer},
        description="Get current authenticated user info"
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Get current user info.
        """
        serializer = UserAuthSerializer(request.user)
        return Response(
            {
                'success': True,
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    @extend_schema(
        description="Refresh access token using refresh token"
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def refresh(self, request):
        """
        Refresh access token using refresh token.
        """
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {
                    'success': False,
                    'message': 'Refresh token is required'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            refresh = RefreshToken(refresh_token)
            return Response(
                {
                    'success': True,
                    'data': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh)
                    }
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'message': 'Invalid refresh token',
                    'error': str(e)
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip
