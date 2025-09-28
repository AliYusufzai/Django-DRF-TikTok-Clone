from rest_framework.response import Response
from rest_framework import generics, status, permissions
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserUpdateSerializer
from .utils import generate_email_verification_token, decode_email_verification_token

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            token = generate_email_verification_token(user)
            verification_link = f"http://localhost:8000/api/v1/auth/verify-email/?token={token}"
            
            send_mail(
                subject="Verify your email",
                message=f"Click here to verify your email: {verification_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            {"success": False, "data": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

class VerifyEmailView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        token = request.query_params.get("token", None)

        if not token:
            return Response(
                {"success": False, "data": {"error": "Token is required"}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            user_id = decode_email_verification_token(token)
            user = get_object_or_404(User, id=user_id)
            if user.is_active:
                return Response(
                    {"success": True, "data": {"message": "Email already verified"}},
                    status=status.HTTP_200_OK,
                )
            
            user.is_active = True
            user.save()

            return Response(
                {"success": True, "data": {"message": "Email verified successfully"}},
                status=status.HTTP_200_OK,
            )
            
        except Exception as e:
            return Response(
                {"success": False, "data": {"error": str(e)}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return Response(
                {"success": True, "data": serializer.validated_data},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": False, "data": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
class UserProfileView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get("id", None)

        try:
            if user_id:
                user = get_object_or_404(User, id=user_id)
            else:
                user = request.user
            serializer = UserRegistrationSerializer(user)

            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"success": False, "data": {"error": str(e)}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
class UserUpdateView(generics.GenericAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )