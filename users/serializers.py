from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from post.serializers import FollowSerializer


User = get_user_model()

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'age', 'password']

    def validate(self, data):
        user = User(**data)
        password = data.get('password')
        try:
            validate_password(password, user)
        except exceptions.ValidationError as e:
            serializer_errors = serializers.as_serializer_error(e)
            raise exceptions.ValidationError(
                {'password': serializer_errors['non_field_errors']}
            )
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            email = validated_data['email'],
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
            age = validated_data['age'],
            password = validated_data['password'],
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()
    reported_posts_count = serializers.SerializerMethodField()

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
    
    def get_reported_posts_count(self, obj):
        return obj.reported_posts.count()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'age', 'is_superuser', 'is_active', 'is_online', 
                  'gender', 'profile_image', 'follower_count', 'following_count', 'followers', 'following', 
                  'country', 'education', 'work', 'reported_posts_count']

class UserAdminSerializer(serializers.ModelSerializer):
    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    reported_posts_count = serializers.SerializerMethodField()

    def get_follower_count(self, obj):
        return obj.get_follower_count()

    def get_following_count(self, obj):
        return obj.get_following_count()
    
    def get_reported_posts_count(self, obj):
        return obj.reported_posts.count()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'age', 'is_superuser', 'is_active',
                  'profile_image', 'follower_count', 'following_count', 'reported_posts_count']

