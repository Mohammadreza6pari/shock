from django.contrib import admin
from .models import User

@admin.action(description="Approve selected users to could access the app")
def approve_users(modeladmin, request, queryset):
    queryset.update(is_approved=True)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "is_approved", "is_active")
    actions = [approve_users]
