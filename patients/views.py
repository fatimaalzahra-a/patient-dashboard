from django.db.models import Count, Avg
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ERVisit, CommunicationEvent, SatisfactionSignal, ContextData, ExperienceFailureIndicator
from .serializers import (
    ERVisitSerializer, CommunicationEventSerializer,
    SatisfactionSignalSerializer, ExperienceFailureIndicatorSerializer, ContextDataSerializer
)


class ERVisitViewSet(viewsets.ModelViewSet):
    queryset = ERVisit.objects.all().order_by('-arrival_ts')
    serializer_class = ERVisitSerializer


class CommunicationEventViewSet(viewsets.ModelViewSet):
    queryset = CommunicationEvent.objects.all()
    serializer_class = CommunicationEventSerializer


class SatisfactionSignalViewSet(viewsets.ModelViewSet):
    queryset = SatisfactionSignal.objects.all()
    serializer_class = SatisfactionSignalSerializer


class ContextDataViewSet(viewsets.ModelViewSet):
    queryset = ContextData.objects.all()
    serializer_class = ContextDataSerializer


class ExperienceFailureIndicatorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ExperienceFailureIndicator.objects.all()
    serializer_class = ExperienceFailureIndicatorSerializer


class KPIStatsView(APIView):
    def get(self, request):
        # 1. Total visits today
        total_visits = ERVisit.objects.count()

        # 2. Average Length of Stay
        avg_los = ERVisit.objects.filter(length_of_stay__isnull=False).aggregate(Avg('length_of_stay'))[
            'length_of_stay__avg']

        # 3. LWBS Count (Left Without Being Seen)
        lwbs_count = ExperienceFailureIndicator.objects.filter(lwbs=True).count()

        # 4. Triage Breakdown
        triage_counts = ERVisit.objects.values('triage_level').annotate(total=Count('triage_level'))

        return Response({
            "total_patients": total_visits,
            "average_stay_duration": str(avg_los) if avg_los else "00:00:00",
            "lwbs_incidents": lwbs_count,
            "triage_summary": triage_counts
        })
