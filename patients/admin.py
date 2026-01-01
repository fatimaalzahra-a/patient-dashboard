from django.contrib import admin
from .models import ERVisit, ContextData, CommunicationEvent, SatisfactionSignal, ExperienceFailureIndicator

# Register your models here.
admin.site.register(ERVisit)
admin.site.register(ContextData)
admin.site.register(CommunicationEvent)
admin.site.register(SatisfactionSignal)
admin.site.register(ExperienceFailureIndicator)