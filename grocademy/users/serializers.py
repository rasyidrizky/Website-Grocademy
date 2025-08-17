from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'balance']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    password2 = serializers.CharField(write_only=True, required=True, label="Confirm Password")

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        # Hash password [cite: 112]
        user.set_password(validated_data['password'])
        user.save()
        return user
    
class AdminUserSerializer(serializers.ModelSerializer):
    """Serializer untuk admin, menampilkan lebih banyak detail."""
    class Meta:
        model = CustomUser
        # Tampilkan field yang relevan untuk admin
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'balance', 'is_staff', 'is_active', 'date_joined'
        ]
        read_only_fields = ['date_joined'] # Hanya bisa dibaca

class UserBalanceSerializer(serializers.Serializer):
    """Serializer untuk menambah (increment) saldo."""
    increment = serializers.DecimalField(max_digits=10, decimal_places=2)