from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from .serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model
# Create your views here.

User = get_user_model()

class RegisterView(APIView):
    def post(self, request):
        data = request.data
        user_serializer = UserCreateSerializer(data=data)
        if not user_serializer.is_valid():
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = user_serializer.create(user_serializer.validated_data)
        user = UserSerializer(user)
        return Response(user.data, status=status.HTTP_201_CREATED)


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
            print(user.id)
            serializer = self.serializer_class(user_obj, data=request.data, partial=True)
            if serializer.is_valid():
                post = serializer.save()
                return Response(status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)        
        except User.DoesNotExist:
            return Response("User not found in the database.", status=status.HTTP_404_NOT_FOUND)


