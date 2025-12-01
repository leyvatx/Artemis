"""
Tests para la sección de Analytics del Dashboard
"""

from django.test import TestCase, Client
from django.urls import reverse


class AnalyticsViewsTest(TestCase):
    """Tests para las vistas de Analytics"""

    def setUp(self):
        """Configuración inicial para los tests"""
        self.client = Client()
        
        # Simular sesión de usuario autenticado
        session = self.client.session
        session['auth_user'] = {
            'id': 1,
            'name': 'Test Supervisor',
            'email': 'supervisor@test.com'
        }
        session.save()

    def test_analytics_main_view(self):
        """Test para la vista principal de Analytics"""
        response = self.client.get(reverse('dashboard:Analytics'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/analytics/analytics.html')

    def test_historical_data_view(self):
        """Test para la vista de Historical Data"""
        response = self.client.get(reverse('dashboard:HistoricalData'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/analytics/historical_data.html')

    def test_anomaly_detection_view(self):
        """Test para la vista de Anomaly Detection"""
        response = self.client.get(reverse('dashboard:AnomalyDetection'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/analytics/anomaly_detection.html')

    def test_ml_predictions_view(self):
        """Test para la vista de ML Predictions"""
        response = self.client.get(reverse('dashboard:MLPredictions'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/analytics/ml_predictions.html')

    def test_recommendations_view(self):
        """Test para la vista de Recommendations"""
        response = self.client.get(reverse('dashboard:Recommendations'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/analytics/recommendations.html')

    def test_analytics_without_authentication(self):
        """Test para verificar que las vistas requieren autenticación"""
        # Eliminar la sesión
        self.client.session.flush()
        
        response = self.client.get(reverse('dashboard:Analytics'))
        # Debería redirigir al login
        self.assertEqual(response.status_code, 302)

    def test_historical_data_with_officer_filter(self):
        """Test para la vista de Historical Data con filtro de oficial"""
        response = self.client.get(
            reverse('dashboard:HistoricalData'),
            {'officer_id': '1'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('selected_officer_id', response.context)

    def test_anomaly_detection_with_officer_filter(self):
        """Test para la vista de Anomaly Detection con filtro de oficial"""
        response = self.client.get(
            reverse('dashboard:AnomalyDetection'),
            {'officer_id': '1'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('selected_officer_id', response.context)

    def test_ml_predictions_with_officer_filter(self):
        """Test para la vista de ML Predictions con filtro de oficial"""
        response = self.client.get(
            reverse('dashboard:MLPredictions'),
            {'officer_id': '1'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('selected_officer_id', response.context)

    def test_recommendations_with_officer_filter(self):
        """Test para la vista de Recommendations con filtro de oficial"""
        response = self.client.get(
            reverse('dashboard:Recommendations'),
            {'officer_id': '1'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('selected_officer_id', response.context)


class AnalyticsURLsTest(TestCase):
    """Tests para las URLs de Analytics"""

    def test_analytics_urls_resolve(self):
        """Verificar que todas las URLs de Analytics se resuelven correctamente"""
        urls = [
            'dashboard:Analytics',
            'dashboard:HistoricalData',
            'dashboard:AnomalyDetection',
            'dashboard:MLPredictions',
            'dashboard:Recommendations',
        ]
        
        for url_name in urls:
            with self.subTest(url=url_name):
                url = reverse(url_name)
                self.assertIsNotNone(url)


class AnalyticsContextTest(TestCase):
    """Tests para el contexto de las vistas de Analytics"""

    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        session = self.client.session
        session['auth_user'] = {
            'id': 1,
            'name': 'Test Supervisor',
            'email': 'supervisor@test.com'
        }
        session.save()

    def test_analytics_context_has_section(self):
        """Verificar que el contexto incluye la sección"""
        response = self.client.get(reverse('dashboard:Analytics'))
        self.assertIn('section', response.context)
        self.assertEqual(response.context['section'], 'analytics')

    def test_historical_data_context_keys(self):
        """Verificar las claves del contexto en Historical Data"""
        response = self.client.get(reverse('dashboard:HistoricalData'))
        expected_keys = ['officers', 'selected_officer_id', 'historical_data', 'section']
        
        for key in expected_keys:
            with self.subTest(key=key):
                self.assertIn(key, response.context)

    def test_anomaly_detection_context_keys(self):
        """Verificar las claves del contexto en Anomaly Detection"""
        response = self.client.get(reverse('dashboard:AnomalyDetection'))
        expected_keys = ['officers', 'selected_officer_id', 'anomalies', 'section']
        
        for key in expected_keys:
            with self.subTest(key=key):
                self.assertIn(key, response.context)

    def test_ml_predictions_context_keys(self):
        """Verificar las claves del contexto en ML Predictions"""
        response = self.client.get(reverse('dashboard:MLPredictions'))
        expected_keys = ['officers', 'selected_officer_id', 'predictions', 'section']
        
        for key in expected_keys:
            with self.subTest(key=key):
                self.assertIn(key, response.context)

    def test_recommendations_context_keys(self):
        """Verificar las claves del contexto en Recommendations"""
        response = self.client.get(reverse('dashboard:Recommendations'))
        expected_keys = ['officers', 'selected_officer_id', 'recommendations', 'section']
        
        for key in expected_keys:
            with self.subTest(key=key):
                self.assertIn(key, response.context)
