from django.urls import path
from .views import RegisterView, RetrieveUserView, UpdateUserView, UserListView, UserBlockView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('me/', RetrieveUserView.as_view()),
    path('update/', UpdateUserView.as_view()),
    path('list/', UserListView.as_view()),
    path('block/<int:pk>/', UserBlockView.as_view()),
]
