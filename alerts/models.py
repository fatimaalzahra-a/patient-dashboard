import uuid
from django.db import models
from django.conf import settings


# Create your models here.

class Alert(models.Model):
    Levels = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ]

    # Matching your status requirement: unread, read, archived
    Status = [
        ('unread', 'Unread'),
        ('read', 'Read'),
        ('archived', 'Archived'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=150)
    description = models.TextField()
    level = models.CharField(max_length=10, choices=Levels, default='info')
    status = models.CharField(max_length=10, choices=Status, default='unread')
    triggered_by = models.CharField(max_length=100)
    triggered_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.title} ({self.level})"


class UserAlert(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_alerts')
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='recipients')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'alert')
        indexes = [models.Index(fields=['user', 'is_read']),]

    def __str__(self):
        return self.alert.title
