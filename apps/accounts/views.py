from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import RegisterSerializer
from .emails import send_verification_email, send_password_reset_email
from .models import CustomUser
from drf_spectacular.utils import extend_schema
from django.utils import timezone
from datetime import timedelta
import uuid

@extend_schema(
    summary="Register new user",
    description="Create a new user account with email and password.",
    tags=["Authentication"],
    request=RegisterSerializer,
)
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_verification_email(user)
            return Response({'message': 'created successfully'}, status=status.HTTP_201_CREATED)
        return Response({"message": "invalid data"}, status= status.HTTP_400_BAD_REQUEST)
@extend_schema(tags=["Authentication"])  
class LoginView(APIView):

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, username=email, password=password)
        if user is None:
            return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
)
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh)  
            })    

@extend_schema(tags=["Authentication"])
class VerifyEmailView(APIView):
    def get(self, request, token): 
        try:
            user = CustomUser.objects.get(verification_token = token)
            user.is_verified = True
            user.save()
            return Response({"message":"Verified"},status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"message": "invalid token"}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=['Authentication'])
class CustomTokenRefreshView(TokenRefreshView):
    pass

@extend_schema(tags=["Authentication"])
class ForgotPasswordView(APIView):
    def post(self, request):
        try:    
            email = request.data.get('email')
            user = CustomUser.objects.get(email= email)
            user.password_reset_token = uuid.uuid4()
            user.password_reset_expiry = timezone.now() + timedelta(hours=1)
            user.save()
            send_password_reset_email(user)
            return Response ({"message":"Password Change link sended"}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"message": "email not found"}, status=status.HTTP_404_NOT_FOUND)

@extend_schema(tags=["Authentication"])
class ResetPasswordView(APIView):
    def post(self,request,token):
        try:
            user = CustomUser.objects.get(password_reset_token =token)
            if user.password_reset_expiry < timezone.now():
                return Response({"message": "token expired"}, status=status.HTTP_400_BAD_REQUEST)
            password = request.data.get('password')
            user.set_password(password)
            user.password_reset_token = None
            user.save()
            return Response({"message": "password changed"}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"message": "invalid token"}, status=status.HTTP_400_BAD_REQUEST)
            
@extend_schema(tags=["Authentication"])
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        if not request.user.check_password(old_password):
            return Response({"message":"wrong password"},status=status.HTTP_400_BAD_REQUEST)
        request.user.set_password(new_password)
        request.user.save()
        return Response({"message": "password changed"}, status=status.HTTP_200_OK)
        
        

            

