from django.urls import path
from .views import ( RegisterView, RetrieveUserView, UpdateUserView, UserListView, UserBlockView, 
                    ChangePasswordView, VerifyEmail, ForgotPasswordView, PasswordResetConfirmView )

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('me/', RetrieveUserView.as_view()),
    path('update/', UpdateUserView.as_view()),
    path('list/', UserListView.as_view()),
    path('block/<int:pk>/', UserBlockView.as_view()),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('email-verify/', VerifyEmail.as_view(), name="email-verify"),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('password-reset-confirm/<str:uidb64>/<str:token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
