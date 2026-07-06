from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    bio=models.TextField()
    profile_picture=models.ImageField(upload_to='profile_pics')
    def __str__(self):
        return f"Profile - {self.user.username}"

class Post(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    content=models.CharField(max_length=1000)
    image=models.ImageField(upload_to='profile_pics')
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username} - {self.content[:30]}"


class Like(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    post=models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username} liked {self.post.user.username}'s post"
    

class Comment(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    post=models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}"

class Follow(models.Model):
    follower=models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    following=models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"

class SavedPost(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_posts')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name= 'saved_by')
    saved_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'post'],
                name='unique_saved_post'
            )
        ]
    def __str__(self):
        return f"{self.user.username} saved {self.post.user.username}'s post"
    

class Notification(models.Model):
    sender=models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_sent')
    receiver=models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_received')
    post=models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    NOTIFICATION_TYPES= [('like', 'Like'), ('comment', 'Comment'), ('follow', 'Follow')]
    notification_type = models.CharField(max_length=20, choices= NOTIFICATION_TYPES)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        if self.notification_type == "like":
            return f"{self.sender.username} liked {self.receiver.username}'s post"
        elif self.notification_type == "comment":
            return f"{self.sender.username} commented on {self.receiver.username}'s post"
        elif self.notification_type == "follow":
            return f"{self.sender.username} started following {self.receiver.username}"
        return f"Notification from {self.sender.username}"