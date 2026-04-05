from .models import CustomUser, Profile
from rest_framework import serializers

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken")
        return value

    def create(self, validated_data):
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        username = validated_data.pop('username')
        validated_data['name'] = f"{first_name} {last_name}".strip()
        validated_data['username'] = username
        return CustomUser.objects.create_user(**validated_data)

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate_username(self, value):
        if not CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("No user found with this username")
        return value

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
        if data["old_password"] == data["new_password"]:
            raise serializers.ValidationError("old password is same as new one")
        return data

class ResetPasswordsSerializer(serializers.Serializer):
    password = serializers.CharField(write_only = True)

class LoginOTPVerifySerializer(serializers.Serializer):
    username = serializers.CharField()
    otp = serializers.CharField()

    def validate_username(self, value):
        if not CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("No user found with this username")
        return value

class ProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        exclude = ['id', 'user']

    def get_profile_picture(self, obj):
        request = self.context.get('request')
        if obj.profile_picture:
            return request.build_absolute_uri(obj.profile_picture.url)
        return None

class UserProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()
    username = serializers.CharField(source='user.username', read_only=True)
    fullname = serializers.CharField(source='user.name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Profile
        fields = ['profile_picture', 'bio', 'address', 'phone_number', 'social_links', 'username', 'fullname', 'email']

    def get_profile_picture(self, obj):
        request = self.context.get('request')
        if obj.profile_picture:
            return request.build_absolute_uri(obj.profile_picture.url)
        return None
