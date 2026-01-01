from django.contrib import admin
from .models import Alert, UserAlert

# Register your models here.
admin.site.register(Alert)
admin.site.register(UserAlert)


