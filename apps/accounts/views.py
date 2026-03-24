from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import RegisterSerializer, LoginSerializer,ForgotPasswordSerializer,ResetPasswordsSerializer, ChangePasswordSerializer,ProfileSerializer
from .emails import send_verification_email, send_password_reset_email
from .models import CustomUser, Profile
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
    serializer_class = RegisterSerializer
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_verification_email(user)
            return Response({'message': 'created successfully'}, status=status.HTTP_201_CREATED)
        return Response({"message": "invalid data"}, status= status.HTTP_400_BAD_REQUEST)
@extend_schema(tags=["Authentication"],    request=LoginSerializer,)  
class LoginView(APIView):
    serializer_class = LoginSerializer
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, username=email, password=password)
            if user is None:
                return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            if not user.is_verified:
                return Response({"message": "Please verify your email first"}, status=status.HTTP_403_FORBIDDEN)
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    tags=["Authentication"],request=None )
class VerifyEmailView(APIView):
    serializer_class = None
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

@extend_schema(tags=["Authentication"], request=ForgotPasswordSerializer)
class ForgotPasswordView(APIView):
    serializer_class = ForgotPasswordSerializer
    def post(self, request):
            serializer = ForgotPasswordSerializer(data = request.data)
            if serializer.is_valid():
                email = serializer.validated_data["email"]
                user = CustomUser.objects.get(email= email)
                user.password_reset_token = uuid.uuid4()
                user.password_reset_expiry = timezone.now() + timedelta(hours=1)
                user.save()
                send_password_reset_email(user)
                return Response ({"message":"Password reset link sent"}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=["Authentication"],request=ResetPasswordsSerializer)
class ResetPasswordView(APIView):
    serializer_class = ResetPasswordsSerializer
    def post(self, request, token):
        serializer = ResetPasswordsSerializer(data=request.data)
        if serializer.is_valid():
            try:
                password = serializer.validated_data["password"]
                user = CustomUser.objects.get(password_reset_token=token)
                if user.password_reset_expiry < timezone.now():
                    return Response({"message": "token expired"}, status=status.HTTP_400_BAD_REQUEST)
                user.set_password(password)
                user.password_reset_token = None
                user.save()
                return Response({"message": "password changed"}, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({"message": "invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                        
@extend_schema(tags=["Authentication"],request=ChangePasswordSerializer)
class ChangePasswordView(APIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    def post(self,request):
        serializer = ChangePasswordSerializer(data= request.data)
        if serializer.is_valid():
            new_password = serializer.validated_data["new_password"]
            old_password =serializer.validated_data["old_password"]
            if not request.user.check_password(old_password):
                return Response({"message": "wrong password"}, status=status.HTTP_400_BAD_REQUEST)
            request.user.set_password(new_password)
            request.user.save()
            return Response({"message": "password changed"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)       
@extend_schema(tags=["Profile"],request=ProfileSerializer)
class ProfileView(APIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request):
        profile = Profile.objects.get(user = request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)
    def patch(self, request):
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile,data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



            

