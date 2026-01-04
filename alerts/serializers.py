from rest_framework import serializers
from .models import Alert, UserAlert



class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = '__all__'


class UserAlertSerializer(serializers.ModelSerializer):
    alert_details = AlertSerializer(source='alert', read_only=True)

    class Meta:
        model = UserAlert
        fields = ['id', 'alert', 'alert_details', 'is_read', 'read_at']