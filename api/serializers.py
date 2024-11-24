from rest_framework import serializers
from .models import Register, AppUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Register
        fields = ['registration_number', 'name', 'email', 'phone', 'category', 'validated', 'validated_at', 'validated_by']


class AppUserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    name = serializers.CharField(max_length=100)



class AppUserTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        if not hasattr(self.user, 'app_user') or not self.user.app_user.is_active:
            raise serializers.ValidationError("This user is not authorized to access the app.")

        return data