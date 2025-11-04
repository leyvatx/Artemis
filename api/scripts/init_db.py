#!/usr/bin/env python
"""
Initialization script for Artemis API
Creates initial data including roles and test users
"""
import os
import sys
import django

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from apps.users.models import Role, User
from apps.biometrics.models import MetricType
from apps.alerts.models import AlertType

def create_roles():
    """Create default roles"""
    roles_data = [
        {
            'name': 'Admin',
            'description': 'Administrator with full access to the system'
        },
        {
            'name': 'Supervisor',
            'description': 'Supervisor who can monitor officers and view reports'
        },
        {
            'name': 'Officer',
            'description': 'Field officer whose biometrics and location are monitored'
        },
        {
            'name': 'Analyst',
            'description': 'Data analyst with read-only access to reports and analytics'
        },
    ]
    
    for role_data in roles_data:
        role, created = Role.objects.get_or_create(
            name=role_data['name'],
            defaults={'description': role_data['description']}
        )
        if created:
            print(f"✓ Created role: {role.name}")
        else:
            print(f"○ Role already exists: {role.name}")
    
    return Role.objects.all()


def create_metric_types():
    """Create default metric types"""
    metrics_data = [
        {
            'name': 'Heart Rate',
            'unit': 'bpm',
            'description': 'Beats per minute',
            'min_value': 40,
            'max_value': 200
        },
        {
            'name': 'Blood Pressure Systolic',
            'unit': 'mmHg',
            'description': 'Systolic blood pressure',
            'min_value': 70,
            'max_value': 180
        },
        {
            'name': 'Blood Pressure Diastolic',
            'unit': 'mmHg',
            'description': 'Diastolic blood pressure',
            'min_value': 40,
            'max_value': 120
        },
        {
            'name': 'Body Temperature',
            'unit': '°C',
            'description': 'Body temperature in Celsius',
            'min_value': 35,
            'max_value': 40
        },
        {
            'name': 'Blood Oxygen Level',
            'unit': '%',
            'description': 'Blood oxygen saturation percentage',
            'min_value': 90,
            'max_value': 100
        },
        {
            'name': 'Stress Level',
            'unit': 'score',
            'description': 'Stress level score from 0-10',
            'min_value': 0,
            'max_value': 10
        },
    ]
    
    for metric_data in metrics_data:
        metric, created = MetricType.objects.get_or_create(
            name=metric_data['name'],
            defaults={
                'unit': metric_data['unit'],
                'description': metric_data['description'],
                'min_value': metric_data.get('min_value'),
                'max_value': metric_data.get('max_value'),
            }
        )
        if created:
            print(f"✓ Created metric type: {metric.name}")
        else:
            print(f"○ Metric type already exists: {metric.name}")


def create_alert_types():
    """Create default alert types"""
    alert_data = [
        {
            'name': 'High Heart Rate',
            'default_level': 'High',
            'description': 'Alert when heart rate exceeds normal range'
        },
        {
            'name': 'High Blood Pressure',
            'default_level': 'High',
            'description': 'Alert when blood pressure is elevated'
        },
        {
            'name': 'Low Blood Oxygen',
            'default_level': 'Critical',
            'description': 'Alert when blood oxygen level is critically low'
        },
        {
            'name': 'High Stress Level',
            'default_level': 'Medium',
            'description': 'Alert when stress level is high'
        },
        {
            'name': 'Abnormal Temperature',
            'default_level': 'High',
            'description': 'Alert for abnormal body temperature'
        },
        {
            'name': 'Location Deviation',
            'default_level': 'Medium',
            'description': 'Alert when officer deviates from assigned area'
        },
        {
            'name': 'Device Offline',
            'default_level': 'Low',
            'description': 'Alert when monitoring device goes offline'
        },
    ]
    
    for alert in alert_data:
        alert_type, created = AlertType.objects.get_or_create(
            name=alert['name'],
            defaults={
                'default_level': alert['default_level'],
                'description': alert['description'],
            }
        )
        if created:
            print(f"✓ Created alert type: {alert_type.name}")
        else:
            print(f"○ Alert type already exists: {alert_type.name}")


def create_superuser():
    """Create default superuser"""
    if not User.objects.filter(email='admin@artemis.local').exists():
        admin_role, _ = Role.objects.get_or_create(
            name='Admin',
            defaults={'description': 'Administrator'}
        )
        
        user = User.objects.create(
            name='Administrator',
            email='admin@artemis.local',
            status='Active',
            role=admin_role,
            is_active=True
        )
        user.set_password('admin123')  # Set a default password
        user.save()
        print(f"✓ Created superuser: {user.email}")
    else:
        print(f"○ Superuser already exists: admin@artemis.local")


def main():
    """Run all initialization tasks"""
    print("\n" + "="*60)
    print("Artemis API - Database Initialization")
    print("="*60 + "\n")
    
    print("Creating roles...")
    create_roles()
    
    print("\nCreating metric types...")
    create_metric_types()
    
    print("\nCreating alert types...")
    create_alert_types()
    
    print("\nCreating superuser...")
    create_superuser()
    
    print("\n" + "="*60)
    print("✓ Initialization completed successfully!")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
