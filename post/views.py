from rest_framework.views import APIView
from rest_framework import permissions, status, generics
from rest_framework.response import Response
from django.db.models import Q

from .serializers import PostSerializer, CommentSerializer, UserSerializer, NotificationSerializer
from .models import Post, Comment, Follow, Notification
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
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                post = serializer.save(author=user, post_img=post_img, content=content)
                for follower in user.followers.all():
                    Notification.objects.create(
                        from_user=user,
                        to_user=follower.follower,
                        post=post,
                        notification_type=Notification.NOTIFICATION_TYPES[1][0],
                    )
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)            
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
            user = request.user
            post_obj = Post.objects.get(pk=pk)
            serializer = self.serializer_class(post_obj, data=request.data, partial=True)
            if serializer.is_valid():
                post = serializer.save()
                # for follower in user.followers.all():
                #     Notification.objects.create(
                #         to_user=follower.follower,
                #         from_user=request.user,
                #         post=post,
                #         notification_type=Notification.NOTIFICATION_TYPES[1][0],
                #     )
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
                if not post.author == user:
                    Notification.objects.create(
                        from_user=user,
                        to_user=post.author,
                        post=post,
                        notification_type=Notification.NOTIFICATION_TYPES[0][0],
                    )                   
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
                Notification.objects.create(
                        from_user=follower,
                        to_user=following,
                        notification_type=Notification.NOTIFICATION_TYPES[2][0],
                    ) 
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
        queryset = User.objects.exclude(Q(id=current_user.id) | Q(followers__follower=current_user))
        return queryset
    

class FollowListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        current_user = self.request.user
        queryset = User.objects.filter(Q(followers__follower=current_user) & ~Q(id=current_user.id))
        return queryset


class CreateCommentView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentSerializer

    def post(self, request, pk, *args, **kwargs):
        try:
            user = request.user
            body = request.data.get('body')
            print(request.data, body)
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                comment = serializer.save(user=user, post_id=pk, body=body)
                if not comment.post.author == user:
                    Notification.objects.create(
                            from_user=user,
                            to_user=comment.post.author,
                            post = comment.post,
                            notification_type=Notification.NOTIFICATION_TYPES[3][0],
                        )
                return Response(status=status.HTTP_201_CREATED)
            else:
                print(serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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


class NotificationsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(to_user=user).exclude(is_seen=True).order_by('-created')

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationsSeenView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer

    def post(self, request, pk, *args, **kwargs):
        try:
            notification = Notification.objects.get(pk=pk)
            notification.is_seen = True
            notification.save()
            return Response(status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response("Not found in database", status=status.HTTP_404_NOT_FOUND)


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, email, *args, **kwargs):
        try:
            profile = User.objects.get(email=email)
            profile_posts = Post.objects.filter(author=profile).exclude(is_deleted=True)
            profile_serializer = UserSerializer(profile)
            post_serializer = PostSerializer(profile_posts, many=True)

            context = {
                'profile_user': profile_serializer.data,
                'profile_posts': post_serializer.data
            }
            return Response(context, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response("User not found in the database", status=status.HTTP_404_NOT_FOUND)

