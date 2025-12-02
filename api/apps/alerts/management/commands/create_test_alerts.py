from django.core.management.base import BaseCommand
from apps.alerts.models import Alert, AlertType
from apps.users.models import User
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Crear alertas de prueba para los oficiales'

    def handle(self, *args, **options):
        # Obtener o crear un AlertType
        alert_type, created = AlertType.objects.get_or_create(
            name='System Alert',
            defaults={'description': 'Sistema de alertas general'}
        )
        
        # Crear alertas para usuarios 57 y 94
        officer_ids = [57, 94]
        levels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        statuses = ['open', 'acknowledged', 'resolved']
        
        descriptions = [
            'Frecuencia cardíaca elevada detectada',
            'Nivel de estrés crítico',
            'Comportamiento anómalo registrado',
            'Actividad inusual en la zona',
            'Alerta de biometría',
            'Desviación de ruta detectada',
        ]
        
        for officer_id in officer_ids:
            try:
                officer = User.objects.get(id=officer_id)
                
                # Crear 3 alertas por oficial
                for i in range(3):
                    alert = Alert.objects.create(
                        user=officer,
                        type=alert_type,
                        description=f"{random.choice(descriptions)} - {officer.name}",
                        level=random.choice(levels),
                        status=random.choice(statuses),
                        created_at=datetime.now() - timedelta(hours=i)
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Alert creada: {alert.id} para {officer.name}')
                    )
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'✗ Usuario {officer_id} no encontrado')
                )
        
        self.stdout.write(
            self.style.SUCCESS('✓ Alertas de prueba creadas exitosamente')
        )

