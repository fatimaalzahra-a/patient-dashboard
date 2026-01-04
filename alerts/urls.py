from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlertViewSet

# Using a single ViewSet to manage the /notifications/ endpoint
router = DefaultRouter()
router.register(r'', AlertViewSet, basename='alerts')

urlpatterns = [
    path('', include(router.urls)),
]