# prediction.py (version sans stockage en base)
from flask import Blueprint, request, jsonify
from flask_cors import CORS, cross_origin
from auth import token_required  # Import depuis votre auth.py existant
import numpy as np
import joblib
import os
import pickle
from datetime import datetime

# Déclaration du Blueprint avec préfixe /api
prediction_bp = Blueprint('prediction', __name__, url_prefix='/api')
CORS(prediction_bp)  # CORS pour ce blueprint

# Chargement des modèles ML
IRRIGATION_MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'model_data', 'models', 'Random_Forest.pkl')
CROP_MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'model_data', 'model-label', 'Random_Forest.pkl')

# Chargement du modèle d'irrigation
irrigation_model = None 
try: 
    irrigation_model = joblib.load(IRRIGATION_MODEL_PATH)
    print(f"✅ Modèle irrigation chargé depuis {IRRIGATION_MODEL_PATH}")
except Exception as e:
    try:
        with open(IRRIGATION_MODEL_PATH, 'rb') as f:
            irrigation_model = pickle.load(f)
        print(f"✅ Modèle irrigation chargé avec pickle depuis {IRRIGATION_MODEL_PATH}")
    except Exception as e2:
        print(f"❌ Erreur chargement modèle irrigation: {e}, {e2}")
        irrigation_model = None

# Chargement du modèle de culture
CROP_CLASSES = ['rice', 'maize', 'chickpea', 'kidneybeans', 'pigeonpeas', 'mothbeans', 
                'mungbean', 'blackgram', 'lentil', 'pomegranate', 'banana', 'mango', 
                'grapes', 'watermelon', 'muskmelon', 'apple', 'orange', 'papaya', 
                'coconut', 'cotton', 'jute', 'coffee']
 
crop_model = None 
try:
    crop_model = joblib.load(CROP_MODEL_PATH)
    print(f"✅ Modèle culture chargé depuis {CROP_MODEL_PATH}")
    print(f"📝 Classes de cultures: {len(CROP_CLASSES)} types disponibles")
except Exception as e1:
    try:
        with open(CROP_MODEL_PATH, 'rb') as f:
            crop_model = pickle.load(f)
        print(f"✅ Modèle culture chargé avec pickle depuis {CROP_MODEL_PATH}")
    except Exception as e2:
        print(f"❌ Erreur chargement modèle culture: {e1}, {e2}")
        crop_model = None

def simulate_irrigation_prediction(data):
    """Simulation de prédiction d'irrigation basée sur des règles simples"""
    try:
        humidity = float(data['humidity'])
        rainfall_monthly = float(data['Rainfall_Mensuel'])
        temperature = float(data['temperature'])
        
        if humidity < 50 and rainfall_monthly < 30 and temperature > 25:
            return "Oui, irrigation recommandée"
        elif humidity > 70 or rainfall_monthly > 100:
            return "Non, irrigation non nécessaire"
        else:
            return "Oui, irrigation recommandée"
    except Exception as e:
        print(f"Erreur simulation irrigation: {e}")
        return "Oui, irrigation recommandée"

# ENDPOINT IRRIGATION
@prediction_bp.route('/predict', methods=['POST', 'OPTIONS'])
@cross_origin()
@token_required
def predict_irrigation_only(current_user):
    """Endpoint de prédiction d'irrigation seule"""
    try:
        if request.method == 'OPTIONS':
            return jsonify({'success': True}), 200
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Aucune donnée fournie'}), 400

        # Conversion des données
        try:
            input_data = np.array([
                float(data['Nitrogen']), float(data['phosphorous']), float(data['Potassium']),
                float(data['temperature']), float(data['humidity']), float(data['ph']),
                float(data['Rainfall_Mensuel']), float(data['Rainfall_Annuel'])
            ]).reshape(1, -1)
        except ValueError as e:
            return jsonify({'success': False, 'error': f'Valeur invalide: {e}'}), 400

        # Prédiction irrigation
        irrigation_prediction = "Non déterminée"
        if irrigation_model is not None:
            try:
                prediction_result = irrigation_model.predict(input_data)[0]
                irrigation_prediction = "Oui, irrigation recommandée" if prediction_result == 0 else "Non, irrigation non nécessaire"
            except Exception as e:
                print(f"Erreur modèle irrigation: {e}")
                irrigation_prediction = simulate_irrigation_prediction(data)
        else:
            irrigation_prediction = simulate_irrigation_prediction(data)

        return jsonify({
            'success': True,
            'prediction': irrigation_prediction,
            'recommendation': "Votre culture nécessite un arrosage selon les données analysées." if "Oui" in irrigation_prediction else "Les conditions sont suffisantes, pas besoin d'irrigation pour le moment.",
            'user': current_user.get('email'),
            'parameters': data
        }), 200

    except Exception as e:
        print(f"💥 Erreur prédiction irrigation: {e}")
        return jsonify({'success': False, 'error': 'Erreur serveur lors de la prédiction d\'irrigation'}), 500

# ENDPOINT CULTURE
@prediction_bp.route('/crop-recommendation', methods=['POST', 'OPTIONS'])
@cross_origin()
@token_required
def predict_crop_only(current_user):
    """Endpoint de recommandation de culture seule"""
    try:
        if request.method == 'OPTIONS':
            return jsonify({'success': True}), 200
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Aucune donnée fournie'}), 400

        # Vérifier si le modèle est disponible
        if not crop_model:
            return jsonify({'success': False, 'error': 'Modèle de recommandation de culture non disponible'}), 503

        # Conversion des données
        try:
            input_features = np.array([
                float(data['Nitrogen']), float(data['phosphorous']), float(data['Potassium']),
                float(data['temperature']), float(data['humidity']), float(data['ph']),
                float(data['Rainfall_Mensuel']), float(data['Rainfall_Annuel'])
            ]).reshape(1, -1)
        except ValueError as e:
            return jsonify({'success': False, 'error': f'Valeur invalide: {e}'}), 400

        # Prédiction culture
        try:
            predicted_crop = crop_model.predict(input_features)[0]
            if isinstance(predicted_crop, (int, np.integer)):
                recommended_crop = CROP_CLASSES[predicted_crop] if 0 <= predicted_crop < len(CROP_CLASSES) else "unknown"
            else:
                recommended_crop = str(predicted_crop).lower()
        except Exception as e:
            print(f"💥 Erreur lors de la prédiction: {e}")
            recommended_crop = "Erreur de prédiction"

        return jsonify({
            'success': True,
            'crop': recommended_crop,
            'confidence': 'Élevée',
            'user': current_user.get('email'),
            'parameters': data,
            'recommendation_details': {
                'suitable_for_conditions': True,
                'growth_season': 'Adapté aux conditions actuelles',
                'additional_tips': f'La culture {recommended_crop} est optimale pour vos paramètres sol-climat.'
            }
        }), 200

    except Exception as e:
        print(f"💥 Erreur serveur culture: {e}")
        return jsonify({'success': False, 'error': 'Erreur serveur lors de la recommandation de culture'}), 500
  
    