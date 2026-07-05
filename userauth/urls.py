from django.urls import path
from .import views


urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.loginn, name='loginn'),
    path('logout/', views.logoutt, name='logout'),
    path('profile/<int:user_id>/', views.Profilee, name='profile'),
    path('create-post/', views.create_post, name='create-post'),
    path('edit-profile/', views.edit_profile, name='edit-profile'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit-post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete-post'),
    path('post/<int:post_id>/like/', views.like_post, name='like-post'),
    path('post/<int:post_id>/create_comment/', views.create_comment, name='create_comment'),
    path('post/<int:comment_id>/delete_comment/', views.delete_comment, name='delete-comment'),
    path('follow/<int:user_id>/', views.follow, name='follow-user'),
    path('save_post/<int:post_id>/', views.save_post, name='save-post'),
    path('saved-post/', views.savedpost, name='saved-post'),
    path('notification/', views.Notifications, name='notification'),
]
