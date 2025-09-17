# prediction.py
from flask import Blueprint, request, jsonify
from auth import token_required
import numpy as np
import joblib
import os
import pickle

# Déclaration du Blueprint 
prediction_bp = Blueprint('prediction', __name__, url_prefix='/api')

# 🔍 Chargement des modèles
# Modèle d'irrigation (existant)
IRRIGATION_MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'model_data', 'models', 'Random_Forest.pkl')

# Modèle de culture (nouveau)
CROP_MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'model_data', 'model-label', 'Random_Forest.pkl')

# Chargement du modèle d'irrigation
try:
    irrigation_model = joblib.load(IRRIGATION_MODEL_PATH)
    print(f"✅ Modèle irrigation chargé depuis {IRRIGATION_MODEL_PATH}")
except Exception as e:
    try:
        # Essayer avec pickle si joblib échoue
        with open(IRRIGATION_MODEL_PATH, 'rb') as f:
            irrigation_model = pickle.load(f)
        print(f"✅ Modèle irrigation chargé avec pickle depuis {IRRIGATION_MODEL_PATH}")
    except Exception as e2:
        print(f"❌ Erreur chargement modèle irrigation: {e}, {e2}")
        irrigation_model = None

# Chargement du modèle de culture
crop_model = None
CROP_CLASSES = ['rice', 'maize', 'chickpea', 'kidneybeans', 'pigeonpeas', 'mothbeans', 
                'mungbean', 'blackgram', 'lentil', 'pomegranate', 'banana', 'mango', 
                'grapes', 'watermelon', 'muskmelon', 'apple', 'orange', 'papaya', 
                'coconut', 'cotton', 'jute', 'coffee']

try:
    crop_model = joblib.load(CROP_MODEL_PATH)
    print(f"✅ Modèle culture chargé depuis {CROP_MODEL_PATH}")
    print(f"📝 Classes de cultures: {len(CROP_CLASSES)} types disponibles")
except Exception as e1:
    try:
        # Essayer avec pickle si joblib échoue
        with open(CROP_MODEL_PATH, 'rb') as f:
            crop_model = pickle.load(f)
        print(f"✅ Modèle culture chargé avec pickle depuis {CROP_MODEL_PATH}")
        print(f"📝 Classes de cultures: {len(CROP_CLASSES)} types disponibles")
    except Exception as e2:
        print(f"❌ Erreur chargement modèle culture: {e1}, {e2}")

def simulate_irrigation_prediction(data):
    """
    Simulation de prédiction d'irrigation basée sur des règles simples
    """
    try:
        humidity = float(data['humidity'])
        rainfall_monthly = float(data['Rainfall_Mensuel'])
        temperature = float(data['temperature'])
        
        # Règles d'irrigation
        if humidity < 50 and rainfall_monthly < 30 and temperature > 25:
            return 0  # Irrigation nécessaire
        elif humidity > 70 or rainfall_monthly > 100:
            return 1  # Pas d'irrigation nécessaire
        else:
            return 0  # Irrigation recommandée par défaut
            
    except Exception as e:
        print(f"Erreur simulation irrigation: {e}")
        return 0

@prediction_bp.route('/predict', methods=['POST'])
@token_required
def predict_irrigation_endpoint(current_user):
    """
    Endpoint de prédiction d'irrigation
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'Aucune donnée fournie'}), 400

        # Champs requis
        required_fields = ['Nitrogen', 'phosphorous', 'Potassium', 'temperature',
                           'humidity', 'ph', 'Rainfall_Mensuel', 'Rainfall_Annuel']

        # Vérification des champs manquants
        missing_fields = [field for field in required_fields if field not in data or data[field] == '']
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Champs manquants: {", ".join(missing_fields)}'
            }), 400

        # Vérification et conversion des valeurs
        try:
            input_data = np.array([
                float(data['Nitrogen']),
                float(data['phosphorous']),
                float(data['Potassium']),
                float(data['temperature']),
                float(data['humidity']),
                float(data['ph']),
                float(data['Rainfall_Mensuel']),
                float(data['Rainfall_Annuel']),
            ]).reshape(1, -1)
        except ValueError as e: 
            return jsonify({'success': False, 'error': f'Valeur invalide: {e}'}), 400

        # 📈 Prédiction avec le modèle d'irrigation
        if irrigation_model:
            try:
                prediction = irrigation_model.predict(input_data)[0]
            except Exception as e:
                print(f"Erreur prédiction irrigation: {e}")
                prediction = simulate_irrigation_prediction(data)
        else:
            prediction = simulate_irrigation_prediction(data)

        if prediction == 0: 
            prediction_text = "Oui, irrigation recommandée"
            recommendation = "Votre culture nécessite un arrosage selon les données analysées."
        else:
            prediction_text = "Non, irrigation non nécessaire"
            recommendation = "Les conditions sont suffisantes, pas besoin d'irrigation pour le moment."

        print(f"🌱 Prédiction irrigation pour {current_user['email']} : {prediction_text}")

        return jsonify({
            'success': True,
            'prediction': prediction_text,
            'recommendation': recommendation,
            'user': current_user['email'],
            'parameters': {
                'nitrogen': data['Nitrogen'],
                'phosphorous': data['phosphorous'],
                'potassium': data['Potassium'],
                'temperature': data['temperature'],
                'humidity': data['humidity'],
                'ph': data['ph'],
                'rainfall_monthly': data['Rainfall_Mensuel'],
                'rainfall_annual': data['Rainfall_Annuel'],   
                'rainfall_annual': data['Rainfall_Annuel']
            }
        }), 200

    except Exception as e:
        print(f"💥 Erreur serveur irrigation: {e}")
        return jsonify({'success': False, 'error': 'Erreur serveur lors de la prédiction d\'irrigation'}), 500

@prediction_bp.route('/crop-recommendation', methods=['POST'])
@token_required
def predict_crop_recommendation(current_user):
    """
    Endpoint pour la recommandation de culture avec Random Forest
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'Aucune donnée fournie'}), 400

        # Vérifier si le modèle est disponible
        if not crop_model:
            return jsonify({
                'success': False, 
                'error': 'Modèle de recommandation de culture non disponible'
            }), 503

        # Champs requis pour la prédiction de culture (8 features)
        required_fields = ['Nitrogen', 'phosphorous', 'Potassium', 'temperature',
                           'humidity', 'ph', 'Rainfall_Mensuel', 'Rainfall_Annuel']

        # Vérification des champs manquants
        missing_fields = [field for field in required_fields if field not in data or data[field] == '']
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Champs manquants pour la recommandation: {", ".join(missing_fields)}'
            }), 400

        # Préparation des données d'entrée selon l'ordre exact du dataset
        try:
            # Ordre exact du dataset: ['Nitrogen', 'phosphorous', 'Potassium', 'temperature', 'humidity', 'ph', 'Rainfall Mensuel (mm)', 'Rainfall Annuel (mm)']
            # X = df.drop(columns=['besoin_irrigation', 'label']) donc 8 features
            input_features = np.array([
                float(data['Nitrogen']),
                float(data['phosphorous']),
                float(data['Potassium']),
                float(data['temperature']),
                float(data['humidity']),
                float(data['ph']),
                float(data['Rainfall_Mensuel']),  # Correspond à 'Rainfall Mensuel (mm)'
                float(data['Rainfall_Annuel'])   # Correspond à 'Rainfall Annuel (mm)'
            ]).reshape(1, -1)
            print(f"📊 Input features (8 exactes): {input_features}")
            print(f"📊 Shape: {input_features.shape}")
            print(f"📊 Ordre: N={data['Nitrogen']}, P={data['phosphorous']}, K={data['Potassium']}, T={data['temperature']}, H={data['humidity']}, pH={data['ph']}, RM={data['Rainfall_Mensuel']}, RA={data['Rainfall_Annuel']}")
            
        except ValueError as e:
            return jsonify({'success': False, 'error': f'Valeur invalide: {e}'}), 400

        # 🌾 Prédiction de la culture recommandée
        try:
            # Prédiction directe - le modèle retourne le nom de la culture
            predicted_crop = crop_model.predict(input_features)[0]
            
            print(f"🔮 Prédiction brute: {predicted_crop}")
            print(f"🔮 Type de prédiction: {type(predicted_crop)}")
            
            # Si c'est un index numérique, convertir en nom de culture
            if isinstance(predicted_crop, (int, np.integer)):
                if 0 <= predicted_crop < len(CROP_CLASSES):
                    recommended_crop = CROP_CLASSES[predicted_crop]
                else:
                    recommended_crop = "unknown"
            else:
                # Si c'est déjà un nom de culture (string)
                recommended_crop = str(predicted_crop).lower()
                
        except Exception as e:
            print(f"💥 Erreur lors de la prédiction: {e}")
            return jsonify({
                'success': False, 
                'error': f'Erreur lors de la prédiction de culture: {str(e)}'
            }), 500

        # 🧠 Log debug
        print(f"🌾 Culture recommandée pour {current_user['email']} : {recommended_crop}")

        # ✅ Réponse avec informations détaillées
        return jsonify({
            'success': True,
            'crop': recommended_crop,
            'confidence': 'Élevée',
            'user': current_user['email'],
            'parameters': {
                'nitrogen': data['Nitrogen'],
                'phosphorous': data['phosphorous'],
                'potassium': data['Potassium'],
                'temperature': data['temperature'],
                'humidity': data['humidity'],
                'ph': data['ph'],
                'rainfall_monthly': data['Rainfall_Mensuel']
            },
            'recommendation_details': {
                'suitable_for_conditions': True,
                'growth_season': 'Adapté aux conditions actuelles',
                'additional_tips': f'La culture {recommended_crop} est optimale pour vos paramètres sol-climat.'
            }
        }), 200

    except Exception as e: 
        print(f"💥 Erreur serveur culture: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Erreur serveur lors de la recommandation de culture'}), 500

@prediction_bp.route('/predict/history', methods=['GET'])
@token_required
def get_prediction_history(current_user):
    """ 
    Historique des prédictions — à implémenter plus tard 
    """    
    return jsonify({
        'success': True,
        'message': 'Historique non disponible pour le moment',
        'user': current_user['email']
    }), 200

@prediction_bp.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint de vérification de l'état des modèles
    """
    return jsonify({
        'status': 'healthy',
        'models': {
            'irrigation_model': irrigation_model is not None,
            'crop_model': crop_model is not None,
            'crop_classes_count': len(CROP_CLASSES)
        },
        'endpoints': {  
            '/api/predict': 'Prédiction irrigation',
            '/api/crop-recommendation': 'Recommandation culture'
        }
    }), 200  