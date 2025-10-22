from rest_framework import serializers
from django.contrib.auth.hashers import make_password, check_password
from .models import User, Role

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        try:
            user = User.objects.get(email=email, status='Active')
            # Verificación simple de password
            
            if check_password(password, user.password_hash):
                return {'user': user}
            else:
                raise serializers.ValidationError('Credenciales inválidas')
        except User.DoesNotExist:
            raise serializers.ValidationError('Usuario no encontrado')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)
    role_name = serializers.CharField(write_only=True, default='Officer')
    
    class Meta:
        model = User
        fields = ['name', 'email', 'password', 'password_confirm', 'role_name']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Las contraseñas no coinciden")
        
        # Verificar que el email no exista
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError("Este email ya está registrado")
            
        return attrs
    
    def create(self, validated_data):
        # Remover campos que no van al modelo
        password = validated_data.pop('password')
        validated_data.pop('password_confirm')
        role_name = validated_data.pop('role_name', 'Officer')
        
        # Obtener o crear el rol
        role, _ = Role.objects.get_or_create(
            name=role_name,
            defaults={'description': f'Rol {role_name}'}
        )
        
        # Crear usuario
        user = User.objects.create(
            name=validated_data['name'],
            email=validated_data['email'],
            password_hash=make_password(password),
            role=role,
            status='Active'
        )

        return user


class UserResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    email = serializers.EmailField()
    role = serializers.CharField(source='role.name', allow_null=True)
    status = serializers.CharField()