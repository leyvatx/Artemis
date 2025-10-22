from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .auth_serializers_simple import LoginSerializer, RegisterSerializer, UserResponseSerializer

from drf_spectacular.utils import extend_schema, OpenApiExample

@extend_schema(
    request=LoginSerializer,
    responses={200: OpenApiExample(
        'Login exitoso',
        value={
            'message': 'Login exitoso',
            'user': {
                'id': 1,
                'name': 'Usuario Test',
                'email': 'test@police.gov',
                'role': 'Officer',
                'status': 'Active'
            }
        }
    )},
    examples=[
        OpenApiExample(
            'Ejemplo de login',
            value={
                'email': 'test@police.gov',
                'password': 'test123'
            },
            request_only=True
        )
    ]
)
class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            user_data = UserResponseSerializer(user).data

            return Response({'message': 'Login exitoso', 'user': user_data}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    request=RegisterSerializer,
    responses={201: OpenApiExample(
        'Usuario registrado exitosamente',
        value={
            'message': 'Usuario registrado exitosamente',
            'user': {
                'id': 2,
                'name': 'Juan Pérez',
                'email': 'juan@police.gov',
                'role': 'Officer',
                'status': 'Active'
            }
        }
    )},
    examples=[
        OpenApiExample(
            'Ejemplo de registro',
            value={
                'name': 'Juan Pérez',
                'email': 'juan@police.gov',
                'password': 'password123',
                'password_confirm': 'password123',
                'role_name': 'Officer'
            },
            request_only=True
        )
    ]
)
class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_data = UserResponseSerializer(user).data

            return Response({'message': 'Usuario registrado exitosamente', 'user': user_data}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)