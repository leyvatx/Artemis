# test_models.py
import pickle

print("Verificando modelos PKL...\n")

# 1. Verificar model_config.pkl
try:
    with open('model_config.pkl', 'rb') as f:
        config = pickle.load(f)
    
    print("model_config.pkl cargado")
    print(f"   Features en config: {len(config.get('feature_columns', []))}")
    print(f"   Features: {config.get('feature_columns', [])}")
    
    # IMPORTANTE: Debe tener estas features de estrés
    expected_features = [
        'heart_rate',
        'hr_rolling_mean_5',
        'hr_rolling_std_5',
        'hr_rolling_mean_10',
        'hr_diff_abs',
        'hr_ratio_to_median',
        'hr_variability',      # ← DEBE ESTAR
        'hr_rapid_changes',    # ← DEBE ESTAR
        'stress_score'         # ← DEBE ESTAR
    ]
    
    has_stress_features = all(f in config.get('feature_columns', []) for f in expected_features)
    
    if has_stress_features:
        print("   Tiene features de estrés")
    else:
        print("   FALTA features de estrés - REGENERAR notebook")
        
except Exception as e:
    print(f"Error cargando config: {e}")

# 2. Verificar Random Forest
try:
    with open('model_random_forest.pkl', 'rb') as f:
        rf_model = pickle.load(f)
    
    print("\nmodel_random_forest.pkl cargado")
    print(f"   Tipo: {type(rf_model)}")
    print(f"   Features esperadas: {rf_model.n_features_in_}")
    
    if rf_model.n_features_in_ == 9:
        print("   Modelo entrenado con features de estrés")
    elif rf_model.n_features_in_ == 6:
        print("   Modelo SIN features de estrés - REGENERAR notebook")
    
except Exception as e:
    print(f"Error cargando RF: {e}")

# 3. Verificar Isolation Forest
try:
    with open('model_isolation_forest.pkl', 'rb') as f:
        iso_model = pickle.load(f)
    print("\nmodel_isolation_forest.pkl cargado")
    print(f"   Tipo: {type(iso_model)}")
except Exception as e:
    print(f"Error cargando IF: {e}")

# 4. Verificar Scalers
try:
    with open('model_scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    print("\nmodel_scaler.pkl cargado")
    print(f"   Features escaladas: {scaler.n_features_in_}")
    
    with open('model_scaler_rf.pkl', 'rb') as f:
        scaler_rf = pickle.load(f)
    print("model_scaler_rf.pkl cargado")
    print(f"   Features escaladas: {scaler_rf.n_features_in_}")
    
except Exception as e:
    print(f"Error cargando scalers: {e}")

print("\n" + "="*60)
print("RESUMEN:")
print("="*60)

# Conclusión
if has_stress_features and rf_model.n_features_in_ == 9:
    print("TODOS LOS MODELOS ESTÁN CORRECTOS Y ACTUALIZADOS")
    print("LISTO PARA USAR EN PRODUCCIÓN")
else:
    print("MODELOS DESACTUALIZADOS")
    print("NECESITAS EJECUTAR model_training.ipynb COMPLETO")
    print("   (Cell > Run All para regenerar todos los .pkl)")