from django.urls import path
from .views import RegisterView, LoginView, VerifyEmailView, CustomTokenRefreshView, ForgotPasswordView, ResetPasswordView, ChangePasswordView, ProfileView, LogOutView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns=[
    path('register/', RegisterView.as_view(),name = "register"),
    path('login/',LoginView.as_view(),name="login"),
    path('verify/<uuid:token>/', VerifyEmailView.as_view(), name='verify'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/<uuid:token>/', ResetPasswordView.as_view(), name='reset_password'),
    path('change-password/', ChangePasswordView.as_view(),name="change-password"),
    path('profile/', ProfileView.as_view(),name="profile"),
    path('logout/',LogOutView.as_view(), name = 'logout'),


]