from django.contrib import admin
from .models import User, UserProfile, UserRole, Permission, Role, RolePermission
# Register your models here.
admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(UserRole)
admin.site.register(Permission)
admin.site.register(Role)

