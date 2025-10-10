from rest_framework import serializers
from .models import User, Role
import hashlib

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        try:
            user = User.objects.get(email=email, status='Active')
            # Verificación simple de password
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            if user.password_hash == password_hash:
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
            password_hash=hashlib.sha256(password.encode()).hexdigest(),
            role=role,
            status='Active'
        )
        
        return user