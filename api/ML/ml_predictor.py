"""
ML Predictor Module for Artemis Health Monitoring System

Proporciona predicciones ML basadas en datos de frecuencia cardíaca.
Calcula scores de estrés, detecta anomalías y clasifica severidad de alertas.

Uso desde Django:
    from ML.ml_predictor import HealthMonitorML
    
    predictor = HealthMonitorML()
    result = predictor.predict(heart_rate=120)
"""

import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional
import warnings
warnings.filterwarnings('ignore')


class HealthMonitorML:
    """
    Clase principal para predicciones ML de salud de oficiales.
    
    Esta clase carga los modelos entrenados y proporciona métodos
    para predecir riesgos y clasificar alertas basándose solo en HR.
    """
    
    def __init__(self, model_dir: Optional[str] = None):
        """
        Inicializa el predictor cargando todos los modelos.
        
        Args:
            model_dir: Directorio donde están los archivos .pkl
                      Si es None, usa el directorio actual
        """
        if model_dir is None:
            model_dir = Path(__file__).parent
        else:
            model_dir = Path(model_dir)
        
        self.model_dir = model_dir
        self._load_models()
        self._validate_models()
    
    def _load_models(self):
        """Carga todos los modelos y configuraciones desde archivos .pkl"""
        try:
            # Cargar modelos ML
            with open(self.model_dir / 'model_isolation_forest.pkl', 'rb') as f:
                self.isolation_forest = pickle.load(f)
            
            with open(self.model_dir / 'model_random_forest.pkl', 'rb') as f:
                self.random_forest = pickle.load(f)
            
            # Cargar scalers
            with open(self.model_dir / 'model_scaler.pkl', 'rb') as f:
                self.scaler = pickle.load(f)
            
            with open(self.model_dir / 'model_scaler_rf.pkl', 'rb') as f:
                self.scaler_rf = pickle.load(f)
            
            # Cargar configuración
            with open(self.model_dir / 'model_config.pkl', 'rb') as f:
                self.config = pickle.load(f)
            
            # Extraer configuraciones importantes
            self.feature_columns = self.config['feature_columns']
            self.alert_labels = self.config['alert_labels']
            self.hr_thresholds = self.config['hr_thresholds']
            self.stress_thresholds = self.config.get('stress_thresholds', {})
            
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"No se encontraron los archivos de modelos en {self.model_dir}. "
                "Asegúrate de ejecutar el notebook model_training.ipynb primero."
            ) from e
        except Exception as e:
            raise RuntimeError(f"Error cargando modelos: {str(e)}") from e
    
    def _validate_models(self):
        """Valida que los modelos cargados sean correctos"""
        required_attrs = [
            'isolation_forest', 'random_forest', 
            'scaler', 'scaler_rf', 'config'
        ]
        
        for attr in required_attrs:
            if not hasattr(self, attr):
                raise ValueError(f"Falta el atributo requerido: {attr}")
    
    def _calculate_features(self, heart_rate: float, 
                          recent_hrs: Optional[list] = None) -> pd.DataFrame:
        """
        Calcula features necesarias a partir de HR.
        
        Args:
            heart_rate: Valor actual de frecuencia cardíaca (bpm)
            recent_hrs: Lista opcional de HRs recientes para rolling features
        
        Returns:
            DataFrame con features calculadas
        """
        # Si no hay historial, usar HR actual para estimaciones
        if recent_hrs is None or len(recent_hrs) == 0:
            recent_hrs = [heart_rate] * 10
        
        # Asegurar que tenemos suficientes valores
        if len(recent_hrs) < 10:
            recent_hrs = [heart_rate] * (10 - len(recent_hrs)) + list(recent_hrs)
        
        # Convertir a array numpy
        hr_array = np.array(recent_hrs[-10:])
        
        # Calcular features básicas
        hr_mean_5 = np.mean(hr_array[-5:])
        hr_std_5 = np.std(hr_array[-5:])
        hr_mean_10 = np.mean(hr_array)
        hr_diff_abs = abs(hr_array[-1] - hr_array[-2]) if len(hr_array) > 1 else 0
        hr_median = np.median(hr_array)
        
        # Calcular features de estrés
        hr_variability = hr_std_5 / hr_mean_5 if hr_mean_5 > 0 else 0
        
        hr_sudden_changes = sum(
            1 for i in range(len(hr_array)-1) 
            if abs(hr_array[i+1] - hr_array[i]) > 20
        )
        hr_rapid_changes = min(hr_sudden_changes, 5)
        
        # Score de estrés (0-100)
        hr_norm = (heart_rate - 40) / (200 - 40)
        hr_norm = np.clip(hr_norm, 0, 1)
        
        # HRV invertido (baja variabilidad = alto estrés)
        hrv_norm = 1 - np.clip(hr_variability * 10, 0, 1)
        
        changes_norm = hr_rapid_changes / 5.0
        
        # Score ponderado
        stress_score = (
            hr_norm * 0.40 +
            hrv_norm * 0.35 +
            changes_norm * 0.25
        ) * 100
        
        features = {
            'heart_rate': heart_rate,
            'hr_rolling_mean_5': hr_mean_5,
            'hr_rolling_std_5': hr_std_5,
            'hr_rolling_mean_10': hr_mean_10,
            'hr_diff_abs': hr_diff_abs,
            'hr_ratio_to_median': heart_rate / hr_median if hr_median > 0 else 1.0,
            'hr_variability': hr_variability,
            'hr_rapid_changes': hr_rapid_changes,
            'stress_score': stress_score
        }
        
        return pd.DataFrame([features])
    
    def _calculate_stress_score(self, heart_rate: float, 
                                recent_hrs: Optional[list] = None) -> Dict[str, Any]:
        """
        Calcula el score de estrés y nivel basado en HR.
        
        Returns:
            Dict con stress_score (0-100), stress_level, high_stress_risk
        """
        if recent_hrs is None or len(recent_hrs) < 5:
            recent_hrs = [heart_rate] * 10
        
        hr_array = np.array(recent_hrs[-10:])
        
        # Calcular indicadores de estrés
        hr_mean_5 = np.mean(hr_array[-5:])
        hr_std_5 = np.std(hr_array[-5:])
        
        hr_variability = hr_std_5 / hr_mean_5 if hr_mean_5 > 0 else 0
        
        # Cambios rápidos
        sudden_changes = sum(
            1 for i in range(len(hr_array)-1) 
            if abs(hr_array[i+1] - hr_array[i]) > 20
        )
        
        # === USAR LA MISMA FÓRMULA QUE _calculate_features ===
        # HR normalizada (0-1) basada en rangos normales (60-100 bpm)
        hr_norm = np.clip((heart_rate - 60) / 40, 0, 2.5)
        
        # HRV normalizada e invertida (menor HRV = más estrés)
        hrv_norm = 1 - np.clip(hr_variability * 10, 0, 1)
        
        # Cambios rápidos normalizados
        changes_norm = sudden_changes / 5.0
        
        # Score ponderado (igual que en _calculate_features)
        stress_score = (
            hr_norm * 0.40 +        # 40% - HR absoluta
            hrv_norm * 0.35 +       # 35% - Variabilidad (invertida)
            changes_norm * 0.25     # 25% - Cambios bruscos
        ) * 100
        
        stress_score = np.clip(stress_score, 0, 100)
        
        # Clasificar nivel de estrés
        if stress_score >= 85:
            stress_level = 'Muy Alto'
        elif stress_score >= 70:
            stress_level = 'Alto'
        elif stress_score >= 50:
            stress_level = 'Moderado'
        elif stress_score >= 30:
            stress_level = 'Bajo'
        else:
            stress_level = 'Muy Bajo'
        
        return {
            'stress_score': float(stress_score),
            'stress_level': stress_level,
            'high_stress_risk': int(stress_score > 70),
            'hr_variability': float(hr_variability),
            'hr_elevated_sustained': int(heart_rate > 100 and hr_mean_5 > 100),
            'hr_rapid_changes': sudden_changes
        }
    
    def _classify_severity(self, heart_rate: float, 
                          alert_probability: float,
                          stress_score: float) -> str:
        """
        Clasifica la severidad de la alerta.
        
        Returns:
            'CRITICAL', 'HIGH', 'MEDIUM', o 'LOW'
        """
        # Casos críticos
        if (heart_rate < self.hr_thresholds['critical_low'] or 
            heart_rate > self.hr_thresholds['critical_high']):
            return 'CRITICAL'
        
        # Casos altos
        if (alert_probability > 0.8 or stress_score > 85 or
            heart_rate < self.hr_thresholds['warning_low'] or 
            heart_rate > self.hr_thresholds['warning_high']):
            return 'HIGH'
        
        # Casos medios
        if alert_probability > 0.5 or stress_score > 50:
            return 'MEDIUM'
        
        return 'LOW'
    
    def _get_hr_zone(self, heart_rate: float) -> str:
        """Clasifica HR en zonas cardíacas"""
        if heart_rate < 60:
            return 'Zone 1 (Muy Baja)'
        elif heart_rate < 100:
            return 'Zone 2 (Baja)'
        elif heart_rate < 120:
            return 'Zone 3 (Moderada)'
        elif heart_rate < 150:
            return 'Zone 4 (Alta)'
        else:
            return 'Zone 5 (Muy Alta)'
    
    def predict(self, heart_rate: float, 
                recent_hrs: Optional[list] = None,
                user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Realiza predicción completa para un valor de HR.
        
        Args:
            heart_rate: Valor de frecuencia cardíaca actual (bpm)
            recent_hrs: Lista opcional de valores HR recientes (últimos 10)
                       para mejorar la precisión de features temporales
            user_id: ID del usuario (opcional, solo para metadatos)
        
        Returns:
            Diccionario con toda la información de predicción:
            {
                'requires_alert': bool,
                'stress_score': float (0-100),
                'stress_level': str,
                'severity': str ('CRITICAL'/'HIGH'/'MEDIUM'/'LOW'),
                'alert_probability': float (0.0-1.0),
                'is_anomaly': bool,
                'hr_zone': str,
                'metadata': {...}
            }
        
        Example:
            >>> predictor = HealthMonitorML()
            >>> result = predictor.predict(heart_rate=130)
            >>> if result['requires_alert']:
            ...     print(f"Alerta {result['severity']}")
            ...     # Backend guarda la alerta en DB
        """
        # Validar input
        if not isinstance(heart_rate, (int, float)) or heart_rate <= 0:
            raise ValueError(f"heart_rate debe ser un número positivo, got: {heart_rate}")
        
        if heart_rate > 300 or heart_rate < 20:
            raise ValueError(f"heart_rate fuera de rango médico válido: {heart_rate}")
        
        # Calcular features
        features_df = self._calculate_features(heart_rate, recent_hrs)
        
        # Calcular stress
        stress_info = self._calculate_stress_score(heart_rate, recent_hrs)
        
        # 1. Detección de anomalías (Isolation Forest)
        X_scaled = self.scaler.transform(features_df[self.feature_columns])
        anomaly_score = self.isolation_forest.decision_function(X_scaled)[0]
        is_anomaly = self.isolation_forest.predict(X_scaled)[0] == -1
        
        # 2. Predicción de alerta (Random Forest)
        X_rf_scaled = self.scaler_rf.transform(features_df[self.feature_columns])
        alert_probability = self.random_forest.predict_proba(X_rf_scaled)[0][1]
        requires_alert = self.random_forest.predict(X_rf_scaled)[0] == 1
        
        # 3. Clasificar severidad
        severity = self._classify_severity(
            heart_rate, 
            alert_probability,
            stress_info['stress_score']
        )
        
        # 4. Zona cardíaca
        hr_zone = self._get_hr_zone(heart_rate)
        
        # Construir resultado
        result = {
            'requires_alert': bool(requires_alert),
            'stress_score': stress_info['stress_score'],
            'stress_level': stress_info['stress_level'],
            'severity': severity,
            'alert_probability': float(alert_probability),
            'is_anomaly': bool(is_anomaly),
            'hr_zone': hr_zone,
            'metadata': {
                'heart_rate': float(heart_rate),
                'anomaly_score': float(anomaly_score),
                'high_stress_risk': stress_info['high_stress_risk'],
                'hr_variability': stress_info['hr_variability'],
                'hr_elevated_sustained': stress_info['hr_elevated_sustained'],
                'hr_rapid_changes': stress_info['hr_rapid_changes'],
                'user_id': user_id,
                'features': features_df[self.feature_columns].to_dict('records')[0]
            }
        }
        
        return result
    
    def batch_predict(self, heart_rates: list, 
                     user_ids: Optional[list] = None) -> list:
        """
        Realiza predicciones para múltiples valores de HR.
        
        Args:
            heart_rates: Lista de valores HR
            user_ids: Lista opcional de IDs de usuario (mismo tamaño que heart_rates)
        
        Returns:
            Lista de diccionarios de predicciones
        """
        if user_ids is None:
            user_ids = [None] * len(heart_rates)
        
        if len(heart_rates) != len(user_ids):
            raise ValueError("heart_rates y user_ids deben tener el mismo tamaño")
        
        results = []
        for hr, uid in zip(heart_rates, user_ids):
            try:
                result = self.predict(hr, user_id=uid)
                results.append(result)
            except Exception as e:
                # En batch, continuar con otros aunque uno falle
                results.append({
                    'error': str(e),
                    'heart_rate': hr,
                    'user_id': uid
                })
        
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Retorna información sobre los modelos cargados.
        Útil para debugging y monitoreo.
        """
        return {
            'model_directory': str(self.model_dir),
            'feature_columns': self.feature_columns,
            'num_features': len(self.feature_columns),
            'hr_thresholds': self.hr_thresholds,
            'stress_thresholds': self.stress_thresholds,
            'alert_labels': self.alert_labels,
            'models_loaded': {
                'isolation_forest': str(type(self.isolation_forest)),
                'random_forest': str(type(self.random_forest)),
                'scaler': str(type(self.scaler)),
                'scaler_rf': str(type(self.scaler_rf))
            }
        }


# Ejemplo de uso
if __name__ == "__main__":
    print("=" * 70)
    print("ARTEMIS ML PREDICTOR - TEST DE FUNCIONALIDAD")
    print("=" * 70)
    
    # Inicializar predictor
    predictor = HealthMonitorML()
    
    # Casos de prueba
    test_cases = [
        {
            'hr': 75,
            'recent': [72, 73, 74, 75, 76, 74, 73, 75, 76, 75],
            'desc': 'Normal en reposo'
        },
        {
            'hr': 130,
            'recent': [120, 125, 128, 130, 132, 128, 130, 131, 129, 130],
            'desc': 'Actividad moderada'
        },
        {
            'hr': 185,
            'recent': [150, 160, 170, 175, 180, 182, 183, 184, 185, 185],
            'desc': 'CRÍTICO - HR muy alta'
        },
        {
            'hr': 35,
            'recent': [38, 37, 36, 35, 34, 35, 36, 35, 35, 35],
            'desc': 'CRÍTICO - HR muy baja'
        }
    ]
    
    print("\n" + "=" * 70)
    print("CASOS DE PRUEBA")
    print("=" * 70)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nCaso {i}: {test['desc']}")
        print(f"   HR: {test['hr']} bpm")
        
        result = predictor.predict(
            heart_rate=test['hr'],
            recent_hrs=test['recent'],
            user_id=i
        )
        
        print(f"\n   Resultados:")
        print(f"   • Requiere alerta: {'SÍ' if result['requires_alert'] else 'NO'}")
        print(f"   • Severidad: {result['severity']}")
        print(f"   • Probabilidad: {result['alert_probability']:.2%}")
        print(f"   • Estrés: {result['stress_score']:.1f}/100 ({result['stress_level']})")
        print(f"   • Anomalía: {'Sí' if result['is_anomaly'] else 'No'}")
        print(f"   • Zona HR: {result['hr_zone']}")
    
    # Info del modelo
    print("\n" + "=" * 70)
    print("INFORMACIÓN DEL MODELO")
    print("=" * 70)
    info = predictor.get_model_info()
    print(f"Features utilizadas: {info['num_features']}")
    print(f"Umbrales HR críticos: {info['hr_thresholds']['critical_low']}-{info['hr_thresholds']['critical_high']} bpm")
    print(f"Umbral estrés alto: {info['stress_thresholds'].get('high_stress_score', 'N/A')}")
    
    print("\nTest completado exitosamente")
    print("=" * 70)
