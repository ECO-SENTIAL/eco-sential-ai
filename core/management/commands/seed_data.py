import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import Camera, DetectionLog, AlertMessage, ForestOfficer


class Command(BaseCommand):
    help = 'Seed the database with sample EcoSentinel data'

    def handle(self, *args, **kwargs):
        self.stdout.write('[EcoSentinel] Seeding database...')

        # Create cameras
        cameras_data = [
            {'name': 'CAM-001', 'location_name': 'Mudumalai Forest Border', 'latitude': 11.5800, 'longitude': 76.6330, 'zone': 'Zone A'},
            {'name': 'CAM-002', 'location_name': 'Bandipur Tiger Reserve', 'latitude': 11.6700, 'longitude': 76.6300, 'zone': 'Zone B'},
            {'name': 'CAM-003', 'location_name': 'Nagarhole Wildlife Corridor', 'latitude': 12.0400, 'longitude': 76.1500, 'zone': 'Zone C'},
            {'name': 'CAM-004', 'location_name': 'Wayanad Village Boundary', 'latitude': 11.6854, 'longitude': 76.1320, 'zone': 'Zone D'},
            {'name': 'CAM-005', 'location_name': 'Coimbatore Forest Edge', 'latitude': 11.0168, 'longitude': 76.9558, 'zone': 'Zone E'},
        ]
        cameras = []
        for cam_data in cameras_data:
            cam, created = Camera.objects.get_or_create(name=cam_data['name'], defaults=cam_data)
            cameras.append(cam)
            if created:
                self.stdout.write(f'  [CAM] Camera: {cam.name}')

        # Create forest officers
        officers_data = [
            {'username': 'officer', 'password': 'ecosentinel123', 'first_name': 'Rajan', 'last_name': 'Kumar',
             'phone': '+91-9876543210', 'zone': 'Zone A', 'designation': 'Range Forest Officer'},
            {'username': 'officer2', 'password': 'ecosentinel123', 'first_name': 'Priya', 'last_name': 'Sharma',
             'phone': '+91-9876543211', 'zone': 'Zone B', 'designation': 'Wildlife Warden'},
            {'username': 'officer3', 'password': 'ecosentinel123', 'first_name': 'Arjun', 'last_name': 'Pillai',
             'phone': '+91-9876543212', 'zone': 'Zone C', 'designation': 'Forest Guard'},
        ]
        officers = []
        for data in officers_data:
            if not User.objects.filter(username=data['username']).exists():
                user = User.objects.create_user(
                    username=data['username'],
                    password=data['password'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                )
                officer = ForestOfficer.objects.create(
                    user=user,
                    phone=data['phone'],
                    zone=data['zone'],
                    designation=data['designation'],
                )
                officers.append(officer)
                self.stdout.write(f'  [OFFICER] {user.get_full_name()}')
            else:
                officer = ForestOfficer.objects.get(user__username=data['username'])
                officers.append(officer)

        # Create admin superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@ecosentinel.com', 'admin123')
            self.stdout.write('  [ADMIN] Admin user created (admin/admin123)')

        # Sample detection data
        animals = ['elephant', 'tiger', 'leopard', 'bear', 'wild_boar', 'deer', 'deer', 'wild_boar']
        severities_map = {
            'elephant': 'critical', 'tiger': 'critical',
            'leopard': 'high', 'bear': 'high',
            'wild_boar': 'medium', 'deer': 'low', 'unknown': 'medium'
        }
        statuses = ['detected', 'verified', 'action_taken', 'detected', 'detected']
        locations = [
            'Village Zone 1 - Mudumalai', 'Forest Border Gate 3', 'Village Zone 3 - Bandipur',
            'Southern Corridor Entry', 'Eastern Buffer Zone', 'River Crossing Point',
            'Coffee Plantation Border', 'Settlement Boundary North',
        ]
        gps_points = [
            (11.580, 76.633), (11.670, 76.630), (12.040, 76.150),
            (11.685, 76.132), (11.017, 76.956), (11.450, 76.730),
            (11.890, 76.400), (11.250, 76.820),
        ]

        if DetectionLog.objects.count() < 5:
            for i in range(25):
                animal = random.choice(animals)
                gps = random.choice(gps_points)
                offset_lat = gps[0] + random.uniform(-0.05, 0.05)
                offset_lng = gps[1] + random.uniform(-0.05, 0.05)
                ts = timezone.now() - timedelta(
                    days=random.randint(0, 6),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                detection = DetectionLog.objects.create(
                    camera=random.choice(cameras),
                    animal_type=animal,
                    confidence=round(random.uniform(0.72, 0.98), 3),
                    gps_lat=round(offset_lat, 5),
                    gps_lng=round(offset_lng, 5),
                    location_name=random.choice(locations),
                    severity=severities_map.get(animal, 'medium'),
                    status=random.choice(statuses),
                    timestamp=ts,
                )
                # Create alert messages
                for officer in officers[:2]:
                    msg = (f"EcoSentinel Alert: {animal.replace('_',' ').title()} detected near "
                           f"{detection.location_name} at GPS ({detection.gps_lat:.4f}, "
                           f"{detection.gps_lng:.4f}). Immediate action required.")
                    AlertMessage.objects.create(
                        detection=detection,
                        sent_to=officer.user.get_full_name(),
                        phone_number=officer.phone,
                        message_body=msg,
                        sent_at=ts + timedelta(seconds=30),
                        delivery_status='simulated',
                    )
            self.stdout.write('  [DATA] Created 25 detection logs with alerts')

        self.stdout.write(self.style.SUCCESS('\nEcoSentinel database seeded successfully!'))
        self.stdout.write('\nLogin Credentials:')
        self.stdout.write('   Forest Officer: officer / ecosentinel123')
        self.stdout.write('   Admin Panel:    admin / admin123')
        self.stdout.write('   URL: http://127.0.0.1:8000/')
