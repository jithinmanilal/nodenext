from rest_framework.views import APIView
from rest_framework import permissions, status, generics
from rest_framework.response import Response
from .serializers import PostSerializer, CommentSerializer, UserSerializer
from .models import Post, Comment, Follow
from users.models import User

# Create your views here.


class PostListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Post.objects.all().exclude(is_deleted=True).order_by('-created_at')
    serializer_class = PostSerializer


class CreatePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostSerializer

    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            post_img = request.data['post_img']
            content = request.data['content']
            Post.objects.create(author=user, post_img=post_img, content=content)
            return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)


class DeletePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            post.is_deleted = True
            post.save()
            return Response(status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response("Not found in database", status=status.HTTP_404_NOT_FOUND)
        

class UpdatePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostSerializer

    def post(self, request, pk):
        try:
            post_obj = Post.objects.get(pk=pk)
            serializer = self.serializer_class(post_obj, data=request.data, partial=True)
            print(request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(status=status.HTTP_200_OK)
            return Response(serializer.errors)
        
        except Post.DoesNotExist:
            return Response("Not found in the database.")


class LikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            user = request.user
            if user in post.likes.all():
                post.likes.remove(user)
                return Response("Like removed", status=status.HTTP_200_OK)
            else:
                post.likes.add(user)
                return Response("Like added", status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response("Post not found", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class FollowView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            following = User.objects.get(pk=pk)
            follower = request.user
            follow_instance = Follow.objects.filter(following=following, follower=follower).first()

            if follow_instance:
                follow_instance.delete()
                return Response("Unfollowed", status=status.HTTP_200_OK)
            else:
                follow = Follow(following=following, follower=follower)
                follow.save()
                return Response("Followed", status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response("User not found", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NetworkListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        current_user = self.request.user
        queryset = User.objects.exclude(pk=current_user.pk).order_by('-first_name')
        return queryset


class CreateCommentView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentSerializer

    def post(self, request, pk, *args, **kwargs):
        try:
            user = request.user
            body = request.data['content']
            Comment.objects.create(user=user, post_id=pk, body=body)
            return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)


class DeleteCommentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            comment = Comment.objects.get(pk=pk, user=request.user)
            comment.delete()                        
            return Response(status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response("Not found in database", status=status.HTTP_404_NOT_FOUND)

