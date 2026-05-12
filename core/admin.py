from django.contrib import admin
from .models import Camera, DetectionLog, AlertMessage, ForestOfficer


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ['name', 'location_name', 'zone', 'is_active']
    list_filter = ['zone', 'is_active']


@admin.register(DetectionLog)
class DetectionLogAdmin(admin.ModelAdmin):
    list_display = ['animal_type', 'confidence', 'timestamp', 'location_name', 'severity', 'status']
    list_filter = ['animal_type', 'severity', 'status']
    search_fields = ['location_name', 'animal_type']


@admin.register(AlertMessage)
class AlertMessageAdmin(admin.ModelAdmin):
    list_display = ['detection', 'sent_to', 'sent_at', 'delivery_status']


@admin.register(ForestOfficer)
class ForestOfficerAdmin(admin.ModelAdmin):
    list_display = ['user', 'zone', 'designation', 'phone', 'is_active']
