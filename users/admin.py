from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "newsletter_subscription"]
    readonly_fields = []
    search_fields = ["user__username", "user__email", "bio"]
    list_filter = [
        "newsletter_subscription",
    ]
    empty_value_display = "null"