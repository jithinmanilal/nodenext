from django.urls import path
from .views import ( PostListView, CreatePostView, DeletePostView, UpdatePostView, LikeView, 
                    CreateCommentView, DeleteCommentView, FollowView, NetworkListView, FollowListView, NotificationsView, 
                    NotificationsSeenView )


urlpatterns = [
    path('', PostListView.as_view()),
    path('create-post/', CreatePostView.as_view(), name='create-post'),
    path('network/', NetworkListView.as_view(), name='to-network'),
    path('following/', FollowListView.as_view(), name='following'),
    path('notifications/', NotificationsView.as_view(), name='notifications'),
    path('notifications-seen/<int:pk>/', NotificationsSeenView.as_view(), name='notifications-seen'),
    path('update-post/<int:pk>/', UpdatePostView.as_view(), name='update-post'),
    path('delete-post/<int:pk>/', DeletePostView.as_view(), name='delete-post'),
    path('like/<int:pk>/', LikeView.as_view(), name='like-post'),
    path('follow/<int:pk>/', FollowView.as_view(), name='follow'),
    path('<int:pk>/comment/', CreateCommentView.as_view(), name='comment-post'),
    path('<int:pk>/delete-comment/', DeleteCommentView.as_view(), name='delete-comment'),
]

