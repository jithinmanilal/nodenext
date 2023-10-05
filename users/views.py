from rest_framework.views import APIView
from rest_framework import permissions, status, generics
from rest_framework.response import Response
from .serializers import ( UserCreateSerializer, UserSerializer, UserAdminSerializer, ChangePasswordSerializer, 
                          EmailVerificationSerializer, MyTokenObtainPairSerializer, ForgotPasswordSerializer, 
                          PasswordResetConfirmSerializer )
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import Util, EmailUtils
import jwt
from django.conf import settings
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import exception_handler
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Create your views here.
class InvalidToken(AuthenticationFailed):
    status_code = 400
    default_detail = "Invalid token"
    default_code = 'invalid'

User = get_user_model()

class RegisterView(APIView):
    def post(self, request):
        data = request.data
        user_serializer = UserCreateSerializer(data=data)
        if not user_serializer.is_valid():
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = user_serializer.create(user_serializer.validated_data)
        user.is_active = False
        user.save()
        serializer = UserSerializer(user)
        user = serializer.data
        # getting tokens
        user_email = User.objects.get(email=user['email'])
        tokens = RefreshToken.for_user(user_email).access_token
        # send email for user verification
        current_site = get_current_site(request).domain
        relative_link = reverse('email-verify')
        absurl = 'http://'+current_site+relative_link+"?token="+str(tokens)
        email_body = 'Hi '+user['first_name'] + \
            ' Use the link below to verify your email \n' + absurl
        data = {'email_body': email_body, 'to_email': user['email'],
                'email_subject': 'Verify your email'}
        Util.send_email(data=data)
        return Response(user, status=status.HTTP_201_CREATED)


class RetrieveUserView(APIView):    
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        user = UserSerializer(user)
        return Response(user.data, status=status.HTTP_200_OK)
    

class UpdateUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def post(self, request):
        try:
            user = request.user
            user_obj = User.objects.get(pk=user.id)
            serializer = self.serializer_class(user_obj, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)        
        except User.DoesNotExist:
            return Response("User not found in the database.", status=status.HTTP_404_NOT_FOUND)


class UserListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserAdminSerializer


class UserBlockView(APIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = UserAdminSerializer

    def post(self, request, pk):
        try:
            user = User.objects.get(id=pk)
            if user.is_active == True:
                user.is_active = False
                user.save()
                 
                # Send logout event to the NotificationConsumer
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "notify_{}".format(user.id),
                    {
                        'type': 'logout_user',
                    }
                )
                return Response("User Blocked", status=status.HTTP_200_OK)
            else:
                user.is_active = True
                user.save()
                return Response("User Allowed", status=status.HTTP_200_OK)
                
        except User.DoesNotExist:
            return Response("User not found", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            old_password = serializer.validated_data.get('old_password')
            new_password = serializer.validated_data.get('new_password')

            # Check if the old password matches
            if not check_password(old_password, user.password):
                return Response({'detail': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

            # Update the password
            user.set_password(new_password)
            user.save()
            return Response({'detail': 'Password successfully changed.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class VerifyEmail(generics.GenericAPIView ):
    serializer_class = EmailVerificationSerializer

    token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)

    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            print(payload)
            user = User.objects.get(id=payload['user_id'])
            if not user.is_online:
                user.is_online = True
                user.is_active = True
                user.save()
            return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)  # Call the parent class's post method
        except InvalidToken as e:
            response = Response({'detail': str(e)}, status=e.status_code)
        return response
    

class ForgotPasswordView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                if not user.is_active():
                    return Response({'detail': 'User with this has been blocked.'}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({'detail': 'User with this email does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

            # Generate a password reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            current_domain = request.build_absolute_uri("/")
            # reset_url = f"{current_domain.rstrip('/')}{reverse('password_reset_confirm', args=[uid, token])}"
            reset_url = f"https://nextnode.jithinmanilal.site/password-reset/{uid}/{token}"

            # Send the reset password email using EmailUtils
            email_subject = 'Reset your password'
            email_body = f'Click the following link to reset your password:\n\n{reset_url}'
            EmailUtils.send_password_reset_email(email_subject, email_body, email)

            return Response({'detail': 'Password reset email sent.'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class PasswordResetConfirmView(APIView):
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, uidb64, token):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            try:
                # Decode the uidb64 to get the user's primary key
                user_id = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=user_id)

                # Check if the token is valid for the user
                if default_token_generator.check_token(user, token):
                    new_password = serializer.validated_data['new_password']

                    # Set the new password and save the user
                    user.set_password(new_password)
                    user.save()

                    return Response({'detail': 'Password successfully reset.'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return Response({'error': 'Invalid user.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)