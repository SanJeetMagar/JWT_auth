# Django Authentication Project — Complete Documentation
### By Sanjeet Magar | Taught Step by Step

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Setup & Installation](#setup--installation)
3. [Project Structure](#project-structure)
4. [Environment Variables (.env)](#environment-variables-env)
5. [Settings.py — Every Line Explained](#settingspy--every-line-explained)
6. [Custom User Model](#custom-user-model)
7. [Serializers](#serializers)
8. [Views](#views)
9. [URLs](#urls)
10. [Email System](#email-system)
11. [JWT Tokens — Full Understanding](#jwt-tokens--full-understanding)
12. [Swagger Documentation](#swagger-documentation)
13. [Problems & Solutions](#problems--solutions)
14. [Full Auth Flow](#full-auth-flow)
15. [API Endpoints Reference](#api-endpoints-reference)

---

## Project Overview

A complete Django REST API authentication system with:
- Register with email verification
- Login with JWT tokens (access + refresh)
- Forgot password / Reset password
- Change password
- Swagger API documentation

---

## Setup & Installation

### Step 1 — Install Poetry
```bash
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
source ~/.bashrc
poetry --version
```

### Step 2 — Create Project
```bash
mkdir authProject && cd authProject
poetry init
```

### Step 3 — Install Dependencies
```bash
poetry add django djangorestframework djangorestframework-simplejwt python-dotenv drf-spectacular
poetry shell
```

### Step 4 — Create Django Project
```bash
django-admin startproject config .
poetry run python manage.py startapp accounts apps/accounts
```

### Step 5 — Fix apps.py
In `apps/accounts/apps.py`:
```python
from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'  # ← must match folder path!
```

**Why?** Django uses `name` to find your app. Without the correct path, Django can't locate it.

---

## Project Structure

```
authProject/
├── apps/
│   └── accounts/
│       ├── migrations/
│       ├── __init__.py
│       ├── apps.py
│       ├── emails.py       ← email sending functions
│       ├── models.py       ← CustomUser model
│       ├── serializers.py  ← data validation
│       ├── urls.py         ← accounts URL routes
│       └── views.py        ← business logic
├── config/
│   ├── __init__.py
│   ├── settings.py         ← project configuration
│   ├── urls.py             ← main URL routes
│   └── wsgi.py
├── .env                    ← secrets (never push to GitHub!)
├── .gitignore
├── manage.py
├── poetry.lock
└── pyproject.toml
```

---

## Environment Variables (.env)

### What is .env?
A plain text file that stores sensitive information (passwords, secret keys) separately from your code. When you push to GitHub, `.env` is ignored so secrets stay on YOUR computer only.

### Create .env
```bash
touch .env
```

### .env contents
```
SECRET_KEY=django-insecure-your-secret-key-here
DEBUG=True
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=youremail@gmail.com
EMAIL_HOST_PASSWORD=yourgoogleapppassword
EMAIL_USE_TLS=True
```

### .gitignore
```
.env
__pycache__/
*.pyc
db.sqlite3
```

### Why no quotes or spaces in .env?
```
SECRET_KEY = "value"   ← WRONG (spaces and quotes)
SECRET_KEY=value       ← CORRECT
```
`.env` files are very strict about format. Spaces and quotes become part of the value!

### Gmail App Password
Never use your real Gmail password. Instead:
1. Go to myaccount.google.com → Security
2. Enable 2-Step Verification
3. Search "App Passwords"
4. Create one for "django-auth"
5. Use that 16-character password in .env (remove spaces!)

---

## Settings.py — Every Line Explained

```python
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()
```

**`load_dotenv()`** — reads your `.env` file and loads all values into memory. Without this, Python doesn't know `.env` exists!

**`import os`** — Python's built-in library for talking to your operating system. We use `os.environ` to access the loaded .env values.

---

```python
BASE_DIR = Path(__file__).resolve().parent.parent
```

**`__file__`** = "this file right here (settings.py)"
**`.resolve()`** = converts relative path to full absolute path (like "123 Main Street" instead of "two blocks up")
**`.parent.parent`** = go up two folders → reaches your project root

---

```python
SECRET_KEY = os.environ.get('SECRET_KEY')
```

**`os.environ`** = a dictionary of all values loaded from .env (like lockers with names)
**`.get('SECRET_KEY')`** = open the locker named 'SECRET_KEY' and return its value

Django uses SECRET_KEY to sign cookies and sessions cryptographically. If stolen, someone can forge login sessions.

---

```python
DEBUG = os.environ.get('DEBUG') == 'True'
```

`.env` stores everything as **strings**. So `'True'` is text, not boolean `True`. Comparing `== 'True'` converts it to a real boolean.

- `DEBUG=True` → `'True' == 'True'` → `True`
- `DEBUG=False` → `'False' == 'True'` → `False`

**Why DEBUG matters?** When `True`, crashes show your entire code to anyone. In production, always `False`!

---

```python
INSTALLED_APPS = [
    'django.contrib.admin',       # /admin panel
    'django.contrib.auth',        # built-in auth system
    'django.contrib.contenttypes',# tracks all your models
    'django.contrib.sessions',    # session management
    'django.contrib.messages',    # flash messages
    'django.contrib.staticfiles', # CSS/JS/images
    'rest_framework',             # Django REST Framework
    'rest_framework_simplejwt',   # JWT token system
    'drf_spectacular',            # Swagger docs
    'apps.accounts',              # OUR app
]
```

**Why list them here?** Django only knows about apps you tell it about. Without listing, no database tables are created, no URLs work.

---

```python
AUTH_USER_MODEL = 'apps.accounts.CustomUser'
```

Tells Django: "Use MY custom user model, not your default one." Must be set BEFORE first migration or migrations break!

Default Django User uses `username`. We want `email`. So we replace it.

---

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
```

**`DEFAULT_AUTHENTICATION_CLASSES`** — when a request comes in, DRF uses this to figure out WHO is making the request. We use JWT — so it reads the `Authorization: Bearer <token>` header and identifies the user.

**`DEFAULT_SCHEMA_CLASS`** — tells Swagger how to read your API and generate docs.

---

```python
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}
```

**Access token** — expires in 30 mins. Used for every API request.
**Refresh token** — expires in 7 days. Used ONLY to get new access tokens.
**ROTATE_REFRESH_TOKENS** — every time you use refresh token, old one dies and new one is given. Stolen refresh tokens become useless after first use!

---

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT'))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS') == 'True'
DEFAULT_FROM_EMAIL = os.environ.get('EMAIL_HOST_USER')
```

**`EMAIL_BACKEND`** — HOW to send emails. `smtp.EmailBackend` sends real emails. For testing use `console.EmailBackend` which just prints to terminal.

**`EMAIL_PORT = int(...)`** — .env stores everything as strings. `int()` converts `'587'` (string) to `587` (number). Django needs a real number to connect!

**`EMAIL_USE_TLS`** — TLS encrypts the email as it travels from your server to Gmail. Without it, email content travels in plain text — anyone monitoring the network can read it.

**`DEFAULT_FROM_EMAIL`** — the "From:" address users see when they receive your emails.

---

```python
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

Every database row needs a unique ID. `BigAutoField` supports up to 9 quintillion IDs — enough for any app!

---

```python
SPECTACULAR_SETTINGS = {
    'TITLE': 'Sanjeet Authentication API',
    'DESCRIPTION': 'Secure JWT Authentication System',
    'VERSION': '1.0.0',
}
```

Customizes the Swagger docs page title and description.

---

## Custom User Model

```python
# apps/accounts/models.py

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()
        return user

class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    is_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(default=uuid.uuid4)
    password_reset_token = models.UUIDField(null=True, blank=True)
    password_reset_expiry = models.DateTimeField(null=True, blank=True)

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
```

### Why AbstractBaseUser instead of models.Model?
`models.Model` = regular database table (no auth features)
`AbstractBaseUser` = gives you authentication superpowers for free:
- `set_password()` — hashes password
- `check_password()` — verifies password
- Works with `authenticate()`
- Works with JWT tokens
- `request.user` works correctly

### Why CustomUserManager?
Django's default manager expects `username`. Since we removed username, we need our own manager that creates users using `email`.

### Why email check in create_user?
Email is our primary login method. Without email, user can never log in. We raise an error immediately rather than letting a broken user into the database.

### Why set_password() not user.password = password?
`set_password()` **hashes** the password using PBKDF2 algorithm. The database stores something like `pbkdf2_sha256$390000$abc123...` — useless to anyone who steals the database.

### Why normalize_email()?
`Test@Gmail.COM` and `test@gmail.com` are the same person but look different to computers. `normalize_email()` converts everything to lowercase so the same person can't register twice with different capitalizations.

### Why uuid4 for tokens?
- uuid1 — uses MAC address + time, reveals machine info
- uuid3/uuid5 — predictable (same input = same output)
- **uuid4** — completely random, 340 trillion trillion trillion possible values, impossible to guess

### Why null=True, blank=True on password_reset_token?
New users haven't forgotten their password yet! The field should be empty by default. Only filled when user clicks "forgot password".

---

## Serializers

```python
# apps/accounts/serializers.py

from .models import CustomUser
from rest_framework import serializers

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["email", "name", "password"]

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found")
        return value


class ResetPasswordsSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, data):
        if data["old_password"] == data["new_password"]:
            raise serializers.ValidationError("Old password is same as new one")
        return data
```

### ModelSerializer vs Serializer
**ModelSerializer** — used when creating/saving to database. Needs `model` in Meta class. Has `save()` method that calls your `create()`.

**Serializer** — used just for validating incoming data. No database interaction. Used for Login, ForgotPassword, ChangePassword.

### Why write_only=True on password?
Password should NEVER be sent back in a response. `write_only=True` means: accept this when data comes IN, but never include it when sending data OUT.

### What does validate_email do?
`validate_FIELDNAME` is a special DRF method. DRF automatically calls it during validation. For `validate_email`, we check if the email exists in the database — if not, raise an error immediately before even reaching the view.

### Why return value in validate_email?
Without `return value`, Django gets `None` back and thinks validation returned nothing. Always return the value!

### What does validate() do?
Cross-field validation — comparing multiple fields together. Here we check if old_password equals new_password. Only runs AFTER all individual fields pass their own validation.

### The serializer flow
```
JSON arrives
    ↓
EmailField() checks email format
    ↓
CharField() checks field is present
    ↓
validate_email() checks user exists
    ↓
validate() checks cross-field rules
    ↓
serializer.is_valid() returns True
    ↓
View gets clean data from serializer.validated_data
```

---

## Views

```python
# apps/accounts/views.py

from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import RegisterSerializer, LoginSerializer, ForgotPasswordSerializer, ResetPasswordsSerializer, ChangePasswordSerializer
from .emails import send_verification_email, send_password_reset_email
from .models import CustomUser
from drf_spectacular.utils import extend_schema
from django.utils import timezone
from datetime import timedelta
import uuid


@extend_schema(summary="Register new user", tags=["Authentication"], request=RegisterSerializer)
class RegisterView(APIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_verification_email(user)
            return Response({'message': 'created successfully'}, status=status.HTTP_201_CREATED)
        return Response({"message": "invalid data"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Authentication"], request=LoginSerializer)
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
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Authentication"], request=None)
class VerifyEmailView(APIView):

    def get(self, request, token):
        try:
            user = CustomUser.objects.get(verification_token=token)
            user.is_verified = True
            user.save()
            return Response({"message": "Verified"}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"message": "invalid token"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Authentication'])
class CustomTokenRefreshView(TokenRefreshView):
    pass


@extend_schema(tags=["Authentication"], request=ForgotPasswordSerializer)
class ForgotPasswordView(APIView):
    serializer_class = ForgotPasswordSerializer

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            user = CustomUser.objects.get(email=email)
            user.password_reset_token = uuid.uuid4()
            user.password_reset_expiry = timezone.now() + timedelta(hours=1)
            user.save()
            send_password_reset_email(user)
            return Response({"message": "Password reset link sent"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Authentication"], request=ResetPasswordsSerializer)
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


@extend_schema(tags=["Authentication"], request=ChangePasswordSerializer)
class ChangePasswordView(APIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            old_password = serializer.validated_data["old_password"]
            new_password = serializer.validated_data["new_password"]
            if not request.user.check_password(old_password):
                return Response({"message": "wrong password"}, status=status.HTTP_400_BAD_REQUEST)
            request.user.set_password(new_password)
            request.user.save()
            return Response({"message": "password changed"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

### Why def post and not def get?
- `GET` — reading/requesting data (opening a webpage, clicking a link)
- `POST` — sending data to server (submitting a form, registering)

Register, Login, ForgotPassword all SEND data → `post`
VerifyEmail just reads a token from URL → `get`

### Why permission_classes = [IsAuthenticated] on ChangePasswordView?
You must be logged in to change your password! `IsAuthenticated` automatically checks for a valid JWT token. If no token → request rejected before the view even runs.

### Why check old_password in ChangePasswordView?
Security! If someone steals your phone while you're logged in, they shouldn't be able to change your password without knowing the old one.

### Why user.password_reset_token = None after reset?
Clears the token so the reset link can't be used again. One-time use only! Security!

### Why timezone.now() + timedelta(hours=1)?
`timezone.now()` = current time
`timedelta(hours=1)` = 1 hour
Together = "1 hour from now"

If user requests reset but doesn't use the link for 2 hours, the link is expired. Hacker can't use an old stolen link!

### Why serializer.errors instead of custom message?
`serializer.errors` automatically generates detailed errors like:
```json
{
    "email": ["Enter a valid email address."],
    "password": ["This field is required."]
}
```
Much better than our generic "invalid data" message!

---

## URLs

```python
# apps/accounts/urls.py

from django.urls import path
from .views import RegisterView, LoginView, VerifyEmailView, ForgotPasswordView, ResetPasswordView, ChangePasswordView
from .views import CustomTokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify/<uuid:token>/', VerifyEmailView.as_view(), name='verify'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/<uuid:token>/', ResetPasswordView.as_view(), name='reset_password'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
]
```

```python
# config/urls.py

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
```

### Why separate urls.py for accounts?
Organization! As your project grows with more apps, having one giant urls.py with 50+ routes is unmanageable. Each app owns its URLs. Main urls.py just points to them.

### What does include() do?
`include('apps.accounts.urls')` tells Django: "for any URL starting with `api/accounts/`, look in accounts/urls.py for the rest."

### What is <uuid:token> in the URL?
Django automatically captures that UUID from the URL and passes it as `token` parameter to the view. `/verify/550e8400-.../` → `token = "550e8400-..."` in your view!

### Why .as_view()?
Our views are **classes** (RegisterView, LoginView...). HTTP needs a **function** to call. `.as_view()` converts the class into a function Django can use.

---

## Email System

```python
# apps/accounts/emails.py

from django.core.mail import send_mail
from django.conf import settings

def send_verification_email(user):
    verification_link = f"http://localhost:8000/api/accounts/verify/{user.verification_token}/"
    send_mail(
        subject='Verify your email',
        message=f'Click this link to verify: {verification_link}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
    )

def send_password_reset_email(user):
    reset_link = f"http://localhost:8000/api/accounts/reset-password/{user.password_reset_token}/"
    send_mail(
        subject='Reset your password',
        message=f'Click this link to reset your password: {reset_link}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
    )
```

### Why send email AFTER save not before?
If email sends successfully but save fails → verification link for non-existent user!
Correct order: validate → save → send email

### Why f-strings for links?
```python
f"http://localhost:8000/verify/{user.verification_token}/"
```
`{user.verification_token}` inserts the actual UUID value. Each user gets a unique link!

---

## JWT Tokens — Full Understanding

### Why two tokens?
If you only had one long-lived token and it was stolen → attacker has access for days/weeks.

With two tokens:
- Access token expires in 30 min → stolen token only useful briefly
- Refresh token gets new access token → no need to login again

### Complete token flow
```
1. User logs in
2. Server creates: access token (30 min) + refresh token (7 days)
3. User sends access token with every request
4. After 30 min, access token expires
5. User sends refresh token to /token/refresh/
6. Server gives NEW access token + NEW refresh token (rotation!)
7. Old refresh token is now dead
8. Repeat
```

### What's inside a JWT token?
Tokens look like: `eyJhbGc...` — this is base64 encoded JSON:
```json
{
    "token_type": "access",
    "exp": 1234567890,
    "user_id": "2"
}
```

### ROTATE_REFRESH_TOKENS security
If hacker steals your refresh token and you use it first → their copy becomes invalid instantly. One-time use!

---

## Swagger Documentation

### Why SpectacularAPIView?
Generates a JSON file describing your entire API. Like the raw data behind the scenes.

### Why SpectacularSwaggerView?
Reads that JSON and displays a beautiful interactive UI. Frontend developers use this to understand your API without asking you anything.

### Why serializer_class on views?
```python
class LoginView(APIView):
    serializer_class = LoginSerializer
```
Tells Swagger "this view uses LoginSerializer — read it to show the correct input fields." Without it, Swagger shows "No parameters" and gives warnings in terminal.

### Why extend_schema?
```python
@extend_schema(tags=["Authentication"], request=LoginSerializer)
```
Groups endpoints in Swagger UI and specifies which serializer shows the request body.

---

## Problems & Solutions

### Problem 1 — SECRET_KEY exposed in code
**Situation:** Django writes SECRET_KEY directly in settings.py
**Problem:** Pushing to GitHub exposes it to the world
**Solution:** Move to `.env`, read with `os.environ.get('SECRET_KEY')`

---

### Problem 2 — DEBUG value wrong type
**Situation:** `os.environ.get('DEBUG')` returns string `'True'` not boolean `True`
**Problem:** Django needs real boolean for DEBUG
**Solution:** `DEBUG = os.environ.get('DEBUG') == 'True'`

---

### Problem 3 — apps/ folder was empty
**Situation:** Used `mkdir apps` to create accounts folder
**Problem:** Empty folder isn't a Django app — no models, views, migrations
**Solution:** `poetry run python manage.py startapp accounts apps/accounts`

---

### Problem 4 — apps.py wrong name
**Situation:** Django wrote `name = 'accounts'` in apps.py
**Problem:** App is inside `apps/` folder so Django can't find it
**Solution:** Change to `name = 'apps.accounts'`

---

### Problem 5 — Email port wrong type
**Situation:** `os.environ.get('EMAIL_PORT')` returns string `'587'`
**Problem:** Django needs integer to connect to SMTP server
**Solution:** `EMAIL_PORT = int(os.environ.get('EMAIL_PORT'))`

---

### Problem 6 — Migrations broken after adding null=True
**Situation:** Added `password_reset_token` without `null=True` first. Migration ran. Then added `null=True`.
**Problem:** Old migration had `default=uuid.uuid4` (not null). Existing user in database had a token. Setting to `None` failed with `NOT NULL constraint`
**Solution:** Delete old migrations and database, recreate fresh:
```bash
rm apps/accounts/migrations/0001_initial.py
rm apps/accounts/migrations/0002_*.py
rm db.sqlite3
poetry run python manage.py makemigrations
poetry run python manage.py migrate
```

---

### Problem 7 — Reset password link opened in browser (GET)
**Situation:** Clicking email link opens browser → GET request. ResetPasswordView only has `post()`
**Problem:** `405 Method Not Allowed`
**Solution:** This is CORRECT behavior! Email links always GET. Frontend handles showing the form. Test with Postman using POST method.

---

### Problem 8 — Swagger warnings in terminal
**Situation:** `Error: unable to guess serializer` for all views
**Problem:** Swagger doesn't know which serializer each view uses
**Solution:** Add `serializer_class = YourSerializer` to each view class

---

### Problem 9 — ChangePasswordView wrong serializer in extend_schema
**Situation:** Copy-pasted `request=ResetPasswordsSerializer` on ChangePasswordView
**Problem:** Swagger shows wrong fields for that endpoint
**Solution:** `request=ChangePasswordSerializer`

---

### Problem 10 — Token expired when testing
**Situation:** Got `Token is expired` error in Postman
**Problem:** Old Bearer token still in Postman Authorization tab from previous session
**Solution:** Login again to get fresh tokens, or change Authorization to "No Auth" for public endpoints

---

## Full Auth Flow

### Register Flow
```
User submits {email, name, password}
    ↓
RegisterSerializer validates format
    ↓
serializer.save() → CustomUserManager.create_user()
    ↓
Password gets hashed with set_password()
    ↓
User saved to database (is_verified=False)
    ↓
send_verification_email() sends link with UUID token
    ↓
Response: "created successfully"
```

### Email Verification Flow
```
User clicks link in email
    ↓
Browser opens GET /api/accounts/verify/{uuid}/
    ↓
VerifyEmailView.get() runs
    ↓
CustomUser.objects.get(verification_token=token)
    ↓
user.is_verified = True
    ↓
user.save()
    ↓
Response: "Verified"
```

### Login Flow
```
User submits {email, password}
    ↓
LoginSerializer validates format
    ↓
authenticate() checks database
    ↓
If wrong → "Invalid credentials" (401)
    ↓
RefreshToken.for_user(user) generates both tokens
    ↓
Response: {access: "eyJ...", refresh: "eyJ..."}
```

### Forgot Password Flow
```
User submits {email}
    ↓
ForgotPasswordSerializer validates email + checks user exists
    ↓
Generate new uuid4() reset token
    ↓
Set expiry = timezone.now() + 1 hour
    ↓
Save to database
    ↓
Send email with reset link containing token
    ↓
Response: "Password reset link sent"
```

### Reset Password Flow
```
User submits {password} with token in URL
    ↓
ResetPasswordsSerializer validates password field
    ↓
Find user by password_reset_token
    ↓
Check if expiry < now (expired?)
    ↓
user.set_password(password) → hashes it
    ↓
user.password_reset_token = None (one-time use!)
    ↓
user.save()
    ↓
Response: "password changed"
```

### Change Password Flow
```
Logged in user submits {old_password, new_password}
    ↓
IsAuthenticated checks JWT token → identifies user
    ↓
ChangePasswordSerializer validates + checks old≠new
    ↓
check_password(old_password) verifies it's correct
    ↓
If wrong → "wrong password" (400)
    ↓
request.user.set_password(new_password)
    ↓
request.user.save()
    ↓
Response: "password changed"
```

---

## API Endpoints Reference

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | /api/accounts/register/ | No | Register new user |
| GET | /api/accounts/verify/{token}/ | No | Verify email |
| POST | /api/accounts/login/ | No | Login, get tokens |
| POST | /api/accounts/token/refresh/ | No | Get new access token |
| POST | /api/accounts/forgot-password/ | No | Send reset email |
| POST | /api/accounts/reset-password/{token}/ | No | Reset password |
| POST | /api/accounts/change-password/ | Yes (Bearer) | Change password |

### Testing with Postman

**Public endpoints:** No auth needed, just send JSON body.

**Protected endpoints (change-password):**
1. Login first to get access token
2. In Postman → Authorization tab → Bearer Token
3. Paste access token
4. Send request

### Swagger UI
Visit `http://localhost:8000/` to see interactive API docs.
Click any endpoint → "Try it out" → fill fields → Execute!

---

## Key Concepts Summary

| Concept | Simple Explanation |
|---------|-------------------|
| .env | Locked drawer for secrets — never pushed to GitHub |
| SECRET_KEY | Master password Django uses to sign cookies |
| JWT Access Token | Short-lived ID badge (30 min) for API access |
| JWT Refresh Token | Long-lived key (7 days) to get new access tokens |
| Token Rotation | Old refresh token dies after use — stolen tokens become useless |
| AbstractBaseUser | Gives your User model authentication superpowers |
| set_password() | Hashes password — even you can't read it after |
| Serializer | Validates incoming data before touching the database |
| ModelSerializer | Serializer that can also save to database |
| is_verified | Boolean tracking if user clicked verification email |
| UUID4 | Completely random 128-bit token — impossible to guess |
| write_only=True | Accept field on input but never return it in response |
| permission_classes | Guards on a view — blocks unauthenticated requests |
| validated_data | Clean, guaranteed-valid data after serializer runs |

---

*Built from scratch, understood line by line. — Sanjeet Magar*