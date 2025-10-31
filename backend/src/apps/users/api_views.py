from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from apps.users.models import BNBUser, UserToken
from apps.users.serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    ChangePasswordSerializer,
    ResendVerificationSerializer,
)


# Custom mixin for conditional authentication on documentation views
class ConditionalLoginRequiredMixin:
    """Mixin that requires login only when DEBUG is False"""

    def dispatch(self, request, *args, **kwargs):
        if not settings.DEBUG:
            # Apply authentication check when not in DEBUG mode
            if not request.user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())
        return super().dispatch(request, *args, **kwargs)


class ProtectedSpectacularAPIView(ConditionalLoginRequiredMixin, SpectacularAPIView):
    """OpenAPI schema view with optional authentication"""
    pass


class ProtectedSpectacularSwaggerView(ConditionalLoginRequiredMixin, SpectacularSwaggerView):
    """Swagger UI view with optional authentication"""
    pass


class ProtectedSpectacularRedocView(ConditionalLoginRequiredMixin, SpectacularRedocView):
    """ReDoc view with optional authentication"""
    pass


class RegisterAPIView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    Sends verification email after successful registration.
    """

    queryset = BNBUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "message": _(
                    "Registration successful! Please check your email to verify your account."
                ),
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginAPIView(APIView):
    """
    API endpoint for user login with JWT token generation.
    Requires email verification before login.
    """

    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        # Authenticate user
        user = authenticate(request, username=email, password=password)

        if user is None:
            return Response(
                {"error": _("Invalid email or password.")},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Check if email is verified
        if not user.is_email_confirmed:
            return Response(
                {
                    "error": _("Please verify your email address before logging in."),
                    "email_verified": False,
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": _("Login successful."),
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_200_OK,
        )


class LogoutAPIView(APIView):
    """
    API endpoint for user logout.
    Blacklists the refresh token.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": _("Refresh token is required.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": _("Logout successful.")}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": _("Invalid token or token already blacklisted.")},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CurrentUserAPIView(generics.RetrieveUpdateAPIView):
    """
    API endpoint to get or update current authenticated user details.
    """

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordAPIView(APIView):
    """
    API endpoint for changing user password.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        # Check old password
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response(
                {"error": _("Old password is incorrect.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Set new password
        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response(
            {"message": _("Password changed successfully.")}, status=status.HTTP_200_OK
        )


class ResendVerificationAPIView(APIView):
    """
    API endpoint to resend verification email.
    """

    permission_classes = [AllowAny]
    serializer_class = ResendVerificationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        try:
            user = BNBUser.objects.get(email=email)

            if user.is_email_confirmed:
                return Response(
                    {
                        "message": _("This email is already verified."),
                        "email_verified": True,
                    },
                    status=status.HTTP_200_OK,
                )

            token = user.refresh_user_token()
            user.send_activation_email(token)

            return Response(
                {"message": _("Verification email has been sent.")},
                status=status.HTTP_200_OK,
            )

        except BNBUser.DoesNotExist:
            # Don't reveal if email exists or not for security
            return Response(
                {
                    "message": _(
                        "If an account exists with this email, a verification link has been sent."
                    )
                },
                status=status.HTTP_200_OK,
            )
