from rest_framework import serializers
from .models import Post, Comment, Follow
from users.models import User

class UserSerializer(serializers.ModelSerializer):
    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()

    def get_follower_count(self, obj):
        return obj.get_follower_count()

    def get_following_count(self, obj):
        return obj.get_following_count()

    def get_followers(self, obj):
        followers = obj.followers.all()
        follower_serializer = FollowSerializer(followers, many=True)
        return follower_serializer.data

    def get_following(self, obj):
        following = obj.following.all()
        following_serializer = FollowSerializer(following, many=True)
        return following_serializer.data

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'age', 'is_superuser', 'is_active', 'is_online', 'gender', 'profile_image', 'follower_count', 'following_count', 'followers', 'following')


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = [ 'id','user', 'body', 'created' ]


class FollowSerializer(serializers.ModelSerializer):
    following = serializers.SlugRelatedField(slug_field='email', queryset=User.objects.all())
    follower = serializers.SlugRelatedField(slug_field='email', queryset=User.objects.all())

    class Meta:
        model = Follow
        fields = ['following', 'follower']


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)
    followers = serializers.SerializerMethodField()

    def get_likes_count(self, obj):
        return obj.total_likes()

    def get_followers(self, obj):
        followers = Follow.objects.filter(following=obj.author).select_related('follower')
        follower_serializer = FollowSerializer(instance=followers, many=True, context=self.context)
        return follower_serializer.data

    class Meta:
        model = Post
        fields = ['id', 'post_img', 'content', 'created_at', 'updated_at', 'likes', 'likes_count', 'author', 'comments', 'followers']

