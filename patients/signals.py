from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ERVisit, ExperienceFailureIndicator


@receiver(post_save, sender=ERVisit)
def update_failure_indicator(sender, instance, **kwargs):
    """
    Triggered every time an ERVisit is saved.
    It creates or updates the failure report automatically.
    """

    is_lwbs = (instance.disposition_type == 'lwbs')

    indicator, created = ExperienceFailureIndicator.objects.get_or_create(visit=instance)

    indicator.lwbs = is_lwbs

    first_comm = instance.communications.order_by('event_ts').first()
    if first_comm:
        indicator.comm_event = first_comm

    indicator.save()
