from django.urls import path
from .views import RegisterView, RetrieveUserView, UpdateUserView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('me/', RetrieveUserView.as_view()),
    path('update/', UpdateUserView.as_view()),
]
