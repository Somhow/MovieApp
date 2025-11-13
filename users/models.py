from django.db import models
from django.contrib.auth.models import User
from core.models import BlogEntry

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar =models.ImageField(upload_to="avatars", default="/avatar/default_avatar.jpg", blank=True, null=True)
    
    newsletter_subscription = models.BooleanField(default=False)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username
    
class SavedPosts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_posts")
    post = models.ForeignKey(BlogEntry, on_delete=models.CASCADE, related_name="savers")
    create_at = models.DateTimeField(auto_now_add=True)