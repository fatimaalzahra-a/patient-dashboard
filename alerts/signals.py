from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from alerts.models import Alert, UserAlert

User = get_user_model()

@receiver(post_save, sender=Alert)
def broadcast_alert(sender, instance, created, **kwargs):
    if created:
        # Broadcast to all active auth
        # filter by group later
        active_users = User.objects.filter(is_active=True)
        user_alerts = [
            UserAlert(user=user, alert=instance)
            for user in active_users
        ]
        # bulk create: 1 trip to the DB instead of one for each active user
        UserAlert.objects.bulk_create(user_alerts)
