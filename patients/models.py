import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class ERVisit(models.Model):
    Triage = [(i, str(i)) for i in range(1, 6)]  # 1 (Critical) to 5 (Non-urgent)

    Section = [
        ('main', 'Main ER'),
        ('fasttrack', 'Fast Track'),
        ('trauma', 'Trauma Bay'),
        ('peds', 'Pediatrics')
    ]

    Dispo = [
        ('admitted', 'Admitted to Hospital'),
        ('discharged', 'Discharged Home'),
        ('lwbs', 'Left Without Being Seen'),
        ('transferred', 'Transferred to Other Facility')
    ]

    Age = [
        ('child', 'Child (0-12)'),
        ('teen', 'Teen (13-17)'),
        ('young_adult', 'Young Adult (18-34)'),
        ('adult', 'Adult (35-64)'),
        ('senior', 'Senior (65+)'),
    ]

    visit_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='er_visits')
    arrival_ts = models.DateTimeField(auto_now_add=True)
    triage_ts = models.DateTimeField(null=True, blank=True)
    first_contact_ts = models.DateTimeField(null=True, blank=True)
    disposition_ts = models.DateTimeField(null=True, blank=True)
    triage_level = models.IntegerField(choices=Triage, null=True, blank=True,
                                       validators=[MinValueValidator(1), MaxValueValidator(5)])
    er_section = models.CharField(max_length=50, choices=Section)
    disposition_type = models.CharField(max_length=50, choices=Dispo, null=True, blank=True)
    length_of_stay = models.DurationField(null=True, blank=True, editable=False)
    revisit_72h = models.BooleanField(default=False)
    age_group = models.CharField(max_length=50, choices=Age, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ('patient', 'arrival_ts')
        indexes = [
            models.Index(fields=['er_section', 'triage_level']),
            models.Index(fields=['disposition_type']),
        ]

    def clean(self):
        if self.arrival_ts and self.disposition_ts:
            if self.disposition_ts < self.arrival_ts:
                raise ValidationError("Disposition cannot be before arrival.")
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.arrival_ts and self.disposition_ts:
            if self.disposition_ts >= self.arrival_ts:
                self.length_of_stay = self.disposition_ts - self.arrival_ts
            else:
                from datetime import timedelta
                self.length_of_stay = timedelta(0)

        super().save(*args, **kwargs)


class CommunicationEvent(models.Model):
    Event = [
        ('initial', 'Initial Contact'),
        ('delay_update', 'Delay/Wait Time Update'),
        ('clinical_update', 'Clinical/Results Update'),
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
    overall_score = models.IntegerField(choices=Score, null=True, blank=True,
                                        validators=[MinValueValidator(1), MaxValueValidator(5)])
    waiting_score = models.IntegerField(choices=Score, null=True, blank=True,
                                        validators=[MinValueValidator(1), MaxValueValidator(5)])
    communication_score = models.IntegerField(choices=Score, null=True, blank=True,
                                              validators=[MinValueValidator(1), MaxValueValidator(5)])
    respect_score = models.IntegerField(choices=Score, null=True, blank=True,
                                        validators=[MinValueValidator(1), MaxValueValidator(5)])
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
    comm_event = models.OneToOneField(CommunicationEvent, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='failure_indicator')
    lwbs = models.BooleanField(default=False)
    time_to_first_contact = models.DurationField(null=True, blank=True, editable=False)
    time_without_communication = models.DurationField(null=True, blank=True, editable=False)
    revisit_reason = models.CharField(max_length=50, choices=Revisit, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['lwbs']),
            models.Index(fields=['time_to_first_contact']),
        ]

    def save(self, *args, **kwargs):
        if self.visit and self.visit.arrival_ts:
            if self.visit.first_contact_ts:
                self.time_to_first_contact = self.visit.first_contact_ts - self.visit.arrival_ts
            if self.comm_event and self.comm_event.event_ts:
                self.time_without_communication = self.comm_event.event_ts - self.visit.arrival_ts

        super().save(*args, **kwargs)
