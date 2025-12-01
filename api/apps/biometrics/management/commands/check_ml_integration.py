"""
Management command para verificar integración ML

Uso:
    python manage.py check_ml_integration
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.biometrics.models import BPM
from apps.biometrics.ml_models import MLPrediction, MLAlert
from apps.biometrics.ml_service import get_ml_service
from apps.users.models import User
import random


class Command(BaseCommand):
    help = 'Verifica que la integración ML esté funcionando correctamente'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-test-data',
            action='store_true',
            help='Crear datos de prueba para demostración',
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='ID del usuario para crear datos de prueba',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('VERIFICACIÓN DE INTEGRACIÓN ML - ARTEMIS'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        # 1. Verificar servicio ML
        self.stdout.write('\n1. Verificando Servicio ML...')
        try:
            ml_service = get_ml_service()
            self.stdout.write(self.style.SUCCESS('   ✓ Servicio ML cargado correctamente'))
            
            # Verificar si está usando mock o ML real
            predictor = ml_service.predictor
            if hasattr(predictor, 'predict'):
                test_prediction = predictor.predict(heart_rate=75)
                if test_prediction.get('metadata', {}).get('mock_mode'):
                    self.stdout.write(self.style.WARNING('   ⚠ Usando Mock ML (modelos no entrenados)'))
                else:
                    self.stdout.write(self.style.SUCCESS('   ✓ Usando ML Real (modelos entrenados)'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ✗ Error cargando servicio ML: {e}'))
            return
        
        # 2. Verificar modelos de BD
        self.stdout.write('\n2. Verificando Modelos de Base de Datos...')
        try:
            bpm_count = BPM.objects.count()
            pred_count = MLPrediction.objects.count()
            alert_count = MLAlert.objects.count()
            
            self.stdout.write(self.style.SUCCESS(f'   ✓ BPM registrados: {bpm_count}'))
            self.stdout.write(self.style.SUCCESS(f'   ✓ Predicciones ML: {pred_count}'))
            self.stdout.write(self.style.SUCCESS(f'   ✓ Alertas ML: {alert_count}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ✗ Error verificando BD: {e}'))
            self.stdout.write(self.style.WARNING('   → Ejecuta: python manage.py migrate biometrics'))
            return
        
        # 3. Verificar usuarios
        self.stdout.write('\n3. Verificando Usuarios...')
        users = User.objects.filter(status='Active')
        if users.exists():
            self.stdout.write(self.style.SUCCESS(f'   ✓ Usuarios activos: {users.count()}'))
            for user in users[:5]:
                self.stdout.write(f'     - {user.name} (ID: {user.id})')
        else:
            self.stdout.write(self.style.WARNING('   ⚠ No hay usuarios activos'))
        
        # 4. Estadísticas recientes
        self.stdout.write('\n4. Estadísticas Recientes (últimas 24h)...')
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(hours=24)
        
        recent_bpm = BPM.objects.filter(created_at__gte=cutoff).count()
        recent_pred = MLPrediction.objects.filter(created_at__gte=cutoff).count()
        recent_alerts = MLAlert.objects.filter(created_at__gte=cutoff).count()
        pending_alerts = MLAlert.objects.filter(status='Pending').count()
        critical_alerts = MLAlert.objects.filter(status='Pending', severity='CRITICAL').count()
        
        self.stdout.write(self.style.SUCCESS(f'   ✓ BPM recibidos: {recent_bpm}'))
        self.stdout.write(self.style.SUCCESS(f'   ✓ Predicciones generadas: {recent_pred}'))
        self.stdout.write(self.style.SUCCESS(f'   ✓ Alertas creadas: {recent_alerts}'))
        
        if pending_alerts > 0:
            self.stdout.write(self.style.WARNING(f'   ⚠ Alertas pendientes: {pending_alerts}'))
        if critical_alerts > 0:
            self.stdout.write(self.style.ERROR(f'   🚨 Alertas CRÍTICAS: {critical_alerts}'))
        
        # 5. Crear datos de prueba si se solicita
        if options['create_test_data']:
            self.stdout.write('\n5. Creando Datos de Prueba...')
            self.create_test_data(options.get('user_id'))
        
        # Resumen final
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('INTEGRACIÓN ML: ✓ OPERACIONAL'))
        self.stdout.write('=' * 70)
        
        # Información adicional
        self.stdout.write('\n📋 Endpoints ML disponibles:')
        self.stdout.write('   - GET  /api/biometrics/predictions/')
        self.stdout.write('   - GET  /api/biometrics/predictions/user/{id}/')
        self.stdout.write('   - GET  /api/biometrics/predictions/user/{id}/risk-summary/')
        self.stdout.write('   - GET  /api/biometrics/alerts/')
        self.stdout.write('   - GET  /api/biometrics/alerts/pending/')
        self.stdout.write('   - GET  /api/biometrics/alerts/critical/')
        self.stdout.write('   - POST /api/biometrics/alerts/{id}/acknowledge/')
        self.stdout.write('   - POST /api/biometrics/alerts/{id}/resolve/')
        
        self.stdout.write('\n📚 Documentación: ML/INTEGRACION_DJANGO.md\n')
    
    def create_test_data(self, user_id=None):
        """Crea datos de prueba para demostración"""
        
        # Obtener o crear usuario de prueba
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'   ✗ Usuario {user_id} no existe'))
                return
        else:
            user = User.objects.filter(status='Active').first()
            if not user:
                self.stdout.write(self.style.ERROR('   ✗ No hay usuarios activos'))
                return
        
        self.stdout.write(f'   Creando datos para: {user.name} (ID: {user.id})')
        
        # Escenarios de prueba
        test_scenarios = [
            {'hr': 75, 'desc': 'Normal en reposo'},
            {'hr': 90, 'desc': 'Actividad ligera'},
            {'hr': 130, 'desc': 'Ejercicio moderado'},
            {'hr': 160, 'desc': 'Estrés alto'},
            {'hr': 185, 'desc': 'CRÍTICO - Muy alto'},
        ]
        
        ml_service = get_ml_service()
        created_count = 0
        alerts_count = 0
        
        for scenario in test_scenarios:
            # Crear BPM
            bpm = BPM.objects.create(
                user=user,
                value=scenario['hr']
            )
            
            # Analizar con ML
            result = ml_service.analyze_bpm(bpm)
            
            if result['success']:
                created_count += 1
                if result['alert_created']:
                    alerts_count += 1
                
                self.stdout.write(
                    f'     ✓ {scenario["desc"]}: {scenario["hr"]} bpm → '
                    f'Estrés {result["stress_score"]:.1f} '
                    f'{"🚨" if result["alert_created"] else "✓"}'
                )
        
        self.stdout.write(self.style.SUCCESS(
            f'\n   ✓ Creados {created_count} registros de prueba'
        ))
        if alerts_count > 0:
            self.stdout.write(self.style.WARNING(
                f'   🚨 Se generaron {alerts_count} alertas'
            ))
