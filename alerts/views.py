from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Alert, UserAlert
from .serializers import AlertSerializer, UserAlertSerializer


class AlertViewSet(viewsets.ModelViewSet):
    """
    Handles all endpoints under /api/notifications/
    """

    def get_queryset(self):
        # GET /api/notifications/ -> List ONLY current user's alerts
        return UserAlert.objects.filter(user=self.request.user).order_by('-alert__triggered_at')

    def get_serializer_class(self):
        # Use UserAlertSerializer for listing/retrieving
        # Use AlertSerializer for creating (POST)
        if self.action == 'create':
            return AlertSerializer
        return UserAlertSerializer

    def create(self, request, *args, **kwargs):
        # POST /api/notifications/ -> Creates a GLOBAL Alert
        # The signal we wrote will then handle broadcasting to UserAlerts
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['patch'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        user_notification = self.get_object()
        user_notification.is_read = True
        user_notification.read_at = timezone.now()
        user_notification.save()
        return Response({'status': 'marked as read'})

    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})