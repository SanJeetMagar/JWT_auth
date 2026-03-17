from .models import CustomUser
from rest_framework import serializers

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["email","name","password"]
    password = serializers.CharField(write_only = True)
    def create(self,validated_data):
        return CustomUser.objects.create_user(**validated_data)
