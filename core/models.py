from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Camera(models.Model):
    name = models.CharField(max_length=100)
    location_name = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()
    zone = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    installed_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.name} - {self.location_name}"

    class Meta:
        ordering = ['name']


class DetectionLog(models.Model):
    ANIMAL_CHOICES = [
        ('elephant', 'Elephant'),
        ('tiger', 'Tiger'),
        ('leopard', 'Leopard'),
        ('bear', 'Bear'),
        ('wild_boar', 'Wild Boar'),
        ('deer', 'Deer'),
        ('unknown', 'Unknown'),
    ]
    STATUS_CHOICES = [
        ('detected', 'Detected'),
        ('verified', 'Verified'),
        ('false_alarm', 'False Alarm'),
        ('action_taken', 'Action Taken'),
    ]
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    camera = models.ForeignKey(Camera, on_delete=models.SET_NULL, null=True, blank=True)
    animal_type = models.CharField(max_length=50, choices=ANIMAL_CHOICES)
    confidence = models.FloatField(default=0.0)
    image = models.ImageField(upload_to='detections/', null=True, blank=True)
    annotated_image = models.ImageField(upload_to='annotated/', null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    gps_lat = models.FloatField()
    gps_lng = models.FloatField()
    location_name = models.CharField(max_length=200, default='Forest Border')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='detected')
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='medium')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.animal_type} detected at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-timestamp']


class AlertMessage(models.Model):
    detection = models.ForeignKey(DetectionLog, on_delete=models.CASCADE, related_name='alerts')
    sent_to = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20, blank=True)
    message_body = models.TextField()
    sent_at = models.DateTimeField(default=timezone.now)
    delivery_status = models.CharField(max_length=20, default='simulated')

    def __str__(self):
        return f"Alert for {self.detection.animal_type} - {self.sent_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-sent_at']


class ForestOfficer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    zone = models.CharField(max_length=50)
    designation = models.CharField(max_length=100, default='Forest Guard')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.zone}"
