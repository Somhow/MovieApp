from django.db import models
from tinymce.models import HTMLField
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    title = models.CharField(max_length=200, null=False, blank=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title}"


class BlogEntry(models.Model):
    title = models.CharField(max_length=250, null=False, blank=False)
    category = models.ForeignKey(
        Category, null=False, blank=False, on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = HTMLField(null=False, blank=False)
    rating = models.FloatField(null=True, blank=True, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
#    favourited = models.BooleanField(null=True)


class Comment(models.Model):
    blog_entry = models.ForeignKey(
        BlogEntry, on_delete=models.CASCADE, related_name="comments"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(null=True, blank=True)
    stars = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
