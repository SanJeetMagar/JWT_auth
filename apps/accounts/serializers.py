from .models import CustomUser, Profile
from rest_framework import serializers

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["email","name","password"]
    password = serializers.CharField(write_only = True)
    def create(self,validated_data):
        return CustomUser.objects.create_user(**validated_data)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    def validate_email(self,value):
        if not CustomUser.objects.filter(email =value).exists():
            raise serializers.ValidationError("No user found")
        return value
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only = True)
    new_password = serializers.CharField(write_only = True)
    def validate(self,data):
        old_password = data.get("old_password")
        new_password = data.get("new_password")
        if data["old_password"] == data["new_password"]:
            raise serializers.ValidationError("old password is same as new one")
        return data
class ResetPasswordsSerializer(serializers.Serializer):
    password = serializers.CharField(write_only = True)

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ['id', 'user']
