from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('detection/', views.detection_view, name='detection'),
    path('map/', views.map_view, name='map'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('history/', views.history_view, name='history'),
    path('about/', views.about_view, name='about'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # REST APIs
    path('api/detections/', views.api_detections, name='api_detections'),
    path('api/alerts/', views.api_alerts, name='api_alerts'),
    path('api/stats/', views.api_stats, name='api_stats'),
    path('api/detections/<int:detection_id>/status/', views.api_update_status, name='api_update_status'),
]
