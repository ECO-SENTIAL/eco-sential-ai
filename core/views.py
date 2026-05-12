import json
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Count
from datetime import timedelta
import os

from .models import Camera, DetectionLog, AlertMessage, ForestOfficer


def home(request):
    total_detections = DetectionLog.objects.count()
    active_cameras = Camera.objects.filter(is_active=True).count()
    alerts_sent = AlertMessage.objects.count()
    recent_detections = DetectionLog.objects.all()[:5]
    context = {
        'total_detections': total_detections,
        'active_cameras': active_cameras,
        'alerts_sent': alerts_sent,
        'recent_detections': recent_detections,
        'animals': DetectionLog.ANIMAL_CHOICES[:6],
    }
    return render(request, 'home.html', context)


def detection_view(request):
    result = None
    if request.method == 'POST' and request.FILES.get('image'):
        uploaded_image = request.FILES['image']
        lat = request.POST.get('latitude', '11.0168')
        lng = request.POST.get('longitude', '76.9558')
        
        # AI Detection simulation
        from ai_model.detector import simulate_detection
        detection_result = simulate_detection(uploaded_image)
        
        # Save to DB
        from django.core.files.base import ContentFile
        detection = DetectionLog(
            animal_type=detection_result['animal_type'],
            confidence=detection_result['confidence'],
            gps_lat=float(lat),
            gps_lng=float(lng),
            location_name=request.POST.get('location_name', 'Forest Border Zone'),
            severity=detection_result['severity'],
            status='detected',
        )
        detection.image.save(uploaded_image.name, ContentFile(uploaded_image.read()))
        detection.save()

        # Save annotated image if available
        if detection_result.get('annotated_bytes'):
            detection.annotated_image.save(
                f"annotated_{uploaded_image.name}",
                ContentFile(detection_result['annotated_bytes'])
            )
            detection.save()

        # Create alert
        officers = ForestOfficer.objects.filter(is_active=True)[:3]
        for officer in officers:
            msg = (f"EcoSentinel Alert: {detection.animal_type.title()} detected near "
                   f"{detection.location_name} at GPS ({lat}, {lng}). Immediate action required.")
            AlertMessage.objects.create(
                detection=detection,
                sent_to=officer.user.get_full_name() or officer.user.username,
                phone_number=officer.phone,
                message_body=msg,
                delivery_status='simulated'
            )

        result = {
            'detected': True,
            'animal': detection.get_animal_type_display(),
            'animal_type': detection.animal_type,
            'confidence': round(detection.confidence * 100, 1),
            'severity': detection.severity,
            'lat': lat,
            'lng': lng,
            'timestamp': detection.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'image_url': detection.image.url if detection.image else None,
            'annotated_url': detection.annotated_image.url if detection.annotated_image else None,
            'detection_id': detection.id,
        }

    cameras = Camera.objects.filter(is_active=True)
    return render(request, 'detection.html', {'result': result, 'cameras': cameras})


def map_view(request):
    detections = DetectionLog.objects.all().order_by('-timestamp')[:100]
    detections_data = []
    for d in detections:
        detections_data.append({
            'id': d.id,
            'animal': d.get_animal_type_display(),
            'animal_type': d.animal_type,
            'lat': d.gps_lat,
            'lng': d.gps_lng,
            'location': d.location_name,
            'confidence': round(d.confidence * 100, 1),
            'severity': d.severity,
            'timestamp': d.timestamp.strftime('%Y-%m-%d %H:%M'),
            'status': d.status,
        })
    cameras = Camera.objects.filter(is_active=True)
    cameras_data = [{'name': c.name, 'lat': c.latitude, 'lng': c.longitude, 'zone': c.zone, 'location': c.location_name} for c in cameras]
    return render(request, 'map.html', {
        'detections_json': json.dumps(detections_data),
        'cameras_json': json.dumps(cameras_data),
    })


@login_required
def dashboard(request):
    recent_alerts = DetectionLog.objects.all()[:10]
    total_today = DetectionLog.objects.filter(timestamp__date=timezone.now().date()).count()
    critical_alerts = DetectionLog.objects.filter(severity='critical').count()
    pending_action = DetectionLog.objects.filter(status='detected').count()

    # Chart data - last 7 days
    labels = []
    counts = []
    for i in range(6, -1, -1):
        day = timezone.now().date() - timedelta(days=i)
        count = DetectionLog.objects.filter(timestamp__date=day).count()
        labels.append(day.strftime('%b %d'))
        counts.append(count)

    # Animal distribution
    animal_dist = DetectionLog.objects.values('animal_type').annotate(count=Count('id'))
    animal_labels = [d['animal_type'].title() for d in animal_dist]
    animal_counts = [d['count'] for d in animal_dist]

    context = {
        'recent_alerts': recent_alerts,
        'total_today': total_today,
        'critical_alerts': critical_alerts,
        'pending_action': pending_action,
        'total_all': DetectionLog.objects.count(),
        'chart_labels': json.dumps(labels),
        'chart_counts': json.dumps(counts),
        'animal_labels': json.dumps(animal_labels),
        'animal_counts': json.dumps(animal_counts),
    }
    return render(request, 'dashboard.html', context)


def history_view(request):
    detections = DetectionLog.objects.all()
    animal_filter = request.GET.get('animal', '')
    severity_filter = request.GET.get('severity', '')
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if animal_filter:
        detections = detections.filter(animal_type=animal_filter)
    if severity_filter:
        detections = detections.filter(severity=severity_filter)
    if status_filter:
        detections = detections.filter(status=status_filter)
    if date_from:
        detections = detections.filter(timestamp__date__gte=date_from)
    if date_to:
        detections = detections.filter(timestamp__date__lte=date_to)

    return render(request, 'history.html', {
        'detections': detections[:100],
        'animal_choices': DetectionLog.ANIMAL_CHOICES,
        'severity_choices': DetectionLog.SEVERITY_CHOICES,
        'status_choices': DetectionLog.STATUS_CHOICES,
        'filters': {
            'animal': animal_filter,
            'severity': severity_filter,
            'status': status_filter,
            'date_from': date_from,
            'date_to': date_to,
        }
    })


def about_view(request):
    return render(request, 'about.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('/dashboard/')
        else:
            error = 'Invalid credentials. Please try again.'
    return render(request, 'login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('/')


# REST API endpoints
def api_detections(request):
    detections = DetectionLog.objects.all()[:20]
    data = [{
        'id': d.id,
        'animal_type': d.animal_type,
        'animal': d.get_animal_type_display(),
        'confidence': round(d.confidence * 100, 1),
        'lat': d.gps_lat,
        'lng': d.gps_lng,
        'location': d.location_name,
        'severity': d.severity,
        'status': d.status,
        'timestamp': d.timestamp.isoformat(),
        'image_url': d.image.url if d.image else None,
    } for d in detections]
    return JsonResponse({'detections': data, 'count': len(data)})


def api_alerts(request):
    alerts = AlertMessage.objects.all()[:20]
    data = [{
        'id': a.id,
        'detection_id': a.detection_id,
        'animal': a.detection.get_animal_type_display(),
        'sent_to': a.sent_to,
        'message': a.message_body,
        'sent_at': a.sent_at.isoformat(),
        'status': a.delivery_status,
    } for a in alerts]
    return JsonResponse({'alerts': data})


def api_stats(request):
    total = DetectionLog.objects.count()
    today = DetectionLog.objects.filter(timestamp__date=timezone.now().date()).count()
    by_animal = list(DetectionLog.objects.values('animal_type').annotate(count=Count('id')))
    return JsonResponse({
        'total_detections': total,
        'today': today,
        'active_cameras': Camera.objects.filter(is_active=True).count(),
        'alerts_sent': AlertMessage.objects.count(),
        'by_animal': by_animal,
    })


@csrf_exempt
def api_update_status(request, detection_id):
    if request.method == 'POST':
        detection = get_object_or_404(DetectionLog, pk=detection_id)
        data = json.loads(request.body)
        detection.status = data.get('status', detection.status)
        detection.save()
        return JsonResponse({'success': True, 'status': detection.status})
    return JsonResponse({'error': 'Method not allowed'}, status=405)
