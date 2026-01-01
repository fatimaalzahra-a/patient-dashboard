import uuid
from django.db import models
from django.conf import settings


# Create your models here.

class ERVisit(models.Model):
    Triage = [(i, str(i)) for i in range(1, 6)]  # 1 (Critical) to 5 (Non-urgent)

    Section = [
        ('Main', 'Main ER'),
        ('FastTrack', 'Fast Track'),
        ('Trauma', 'Trauma Bay'),
        ('Peds', 'Pediatrics')
    ]

    Dispo = [
        ('Admitted', 'Admitted to Hospital'),
        ('Discharged', 'Discharged Home'),
        ('LWBS', 'Left Without Being Seen'),
        ('Transferred', 'Transferred to Other Facility')
    ]

    visit_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='er_visits')
    arrival_ts = models.DateTimeField()
    triage_ts = models.DateTimeField(null=True, blank=True)
    first_contact_ts = models.DateTimeField(null=True, blank=True)
    disposition_ts = models.DateTimeField(null=True, blank=True)
    triage_level = models.IntegerField(choices=Triage, null=True, blank=True)
    er_section = models.CharField(max_length=50, choices=Section)
    disposition_type = models.CharField(max_length=50, choices=Dispo, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ('patient', 'arrival_ts')
        indexes = [
            models.Index(fields=['er_section', 'triage_level']),
            models.Index(fields=['disposition_type']),
        ]


class CommunicationEvent(models.Model):
    Event = [
        ('initial', 'Initial Contact'),
        ('delay_update', 'Delay/Wait Time Update'),
        ('clinical_update', 'Clinical/Results Update'),
        ('disposition_plan', 'Disposition/Discharge Plan'),
        ('other', 'Other'),
    ]

    Roles = [
        ('nurse', 'Nurse'),
        ('physician', 'Physician'),
        ('admin', 'Admin')
    ]

    Initiator = [
        ('staff', 'Staff Proactive'),
        ('patient', 'Patient/Family Request'),
    ]

    event_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    visit = models.ForeignKey(ERVisit, on_delete=models.CASCADE, related_name='communications')
    event_type = models.CharField(max_length=50, choices=Event, default='initial')
    event_ts = models.DateTimeField(auto_now_add=True)
    staff_role = models.CharField(max_length=20, choices=Roles)
    initiated_by = models.CharField(max_length=20, choices=Initiator)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['visit', 'event_ts']),
            models.Index(fields=['event_type']),
        ]


class SatisfactionSignal(models.Model):
    Score = [(i, str(i)) for i in range(1, 6)]

    feedback_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    visit = models.ForeignKey(ERVisit, on_delete=models.CASCADE, related_name='signals')
    overall_score = models.IntegerField(choices=Score, null=True, blank=True)
    waiting_score = models.IntegerField(choices=Score, null=True, blank=True)
    communication_score = models.IntegerField(choices=Score, null=True, blank=True)
    respect_score = models.IntegerField(choices=Score, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['overall_score', 'waiting_score']),
        ]


class ContextData(models.Model):
    Shift = [
        ('day', 'Day (07:00 - 15:00)'),
        ('evening', 'Evening (15:00 - 23:00)'),
        ('night', 'Night (23:00 - 07:00)'),
    ]

    Staffing = [
        ('low', 'Low Staffing'),
        ('medium', 'Normal Staffing'),
        ('high', 'Full Staffing'),
    ]

    Capacity = [
        ('under', 'Under Capacity'),
        ('at', 'At Capacity'),
        ('over', 'Over Capacity'),
    ]
    Section = [
        ('Main', 'Main ER'),
        ('FastTrack', 'Fast Track'),
        ('Trauma', 'Trauma Bay'),
        ('Peds', 'Pediatrics')
    ]

    context_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shift = models.CharField(max_length=50, choices=Shift, default='day')
    staffing_level = models.CharField(max_length=50, choices=Staffing, default='medium')
    er_capacity_level = models.CharField(max_length=50, choices=Capacity, default='at')
    date = models.DateField(auto_now_add=True)
    er_section = models.CharField(max_length=50, choices=Section)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ('date', 'shift', 'er_section')
        indexes = [
            models.Index(fields=['date', 'er_section']),
        ]


class ExperienceFailureIndicator(models.Model):
    Revisit = [
        ('worsening', 'Symptoms Worsened'),
        ('new_issue', 'New Unrelated Issue'),
        ('planned', 'Planned Follow-up'),
    ]

    indicator_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    visit = models.OneToOneField(ERVisit, on_delete=models.CASCADE, related_name='failure_report')
    lwbs = models.BooleanField(default=False)
    time_to_first_contact = models.DurationField(null=True, blank=True)
    revisit_reason = models.CharField(max_length=50, choices=Revisit, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['lwbs']),
        ]
