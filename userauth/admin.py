from django.contrib import admin
from django.contrib.auth.models import User
from .models import Profile
from .models import Post
from .models import Like
from .models import Comment
from .models import Follow
from .models import SavedPost
from .models import Notification

# Register your models here.
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(Follow)
admin.site.register(SavedPost)
admin.site.register(Notification)