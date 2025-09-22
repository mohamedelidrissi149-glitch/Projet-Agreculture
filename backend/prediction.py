# prediction.py
from flask import Blueprint, request, jsonify
from flask_cors import CORS, cross_origin
from auth import token_required  # Import depuis votre auth.py existant
from db import Database
from datetime import datetime
import numpy as np
import joblib
import os
import pickle
from bson import ObjectId

# Déclaration du Blueprint avec CORS
prediction_bp = Blueprint('prediction', __name__)
CORS(prediction_bp)  # Ajout du CORS pour ce blueprint

# Initialisation de la base de données
db = Database()
predictions_collection = db.get_collection('predictions')

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
    """
    Simulation de prédiction d'irrigation basée sur des règles simples
    """
    try:
        humidity = float(data['humidity'])
        rainfall_monthly = float(data['Rainfall_Mensuel'])
        temperature = float(data['temperature'])
        
        # Règles d'irrigation
        if humidity < 50 and rainfall_monthly < 30 and temperature > 25:
            return "Oui"  # Irrigation nécessaire
        elif humidity > 70 or rainfall_monthly > 100:
            return "Non"  # Pas d'irrigation nécessaire
        else:
            return "Oui"  # Irrigation recommandée par défaut
            
    except Exception as e:
        print(f"Erreur simulation irrigation: {e}")
        return "Oui"

def get_user_id_from_current_user(current_user):
    """
    Extrait l'ID utilisateur du token décodé - adaptation selon votre structure auth
    """
    # Adaptation selon votre structure d'auth
    if '_id' in current_user:
        return str(current_user['_id'])
    elif 'id' in current_user:
        return str(current_user['id'])
    elif 'user_id' in current_user:
        return str(current_user['user_id'])
    else:
        # Fallback - utiliser l'email comme identifiant unique
        return current_user.get('email', 'unknown')

def save_prediction_to_db(current_user, form_data, irrigation_pred, crop_pred):
    """
    Sauvegarde automatique de la prédiction en base MongoDB
    """
    try:
        if predictions_collection is None:
            print("❌ Collection predictions non disponible")
            return None
            
        # Obtenir l'ID utilisateur
        user_id = get_user_id_from_current_user(current_user)
        
        # Structure du document selon vos spécifications exactes
        prediction_document = {
            'id_agriculteur': user_id,
            'email_agriculteur': current_user.get('email', ''),
            'nom_agriculteur': current_user.get('nom', current_user.get('name', '')),
            'prenom_agriculteur': current_user.get('prenom', current_user.get('firstname', '')),
            
            # Données du sol et climatiques (selon votre formulaire)
            'azote_n': float(form_data['Nitrogen']),
            'phosphore_p': float(form_data['phosphorous']),
            'potassium_k': float(form_data['Potassium']),
            'temperature_celsius': float(form_data['temperature']),
            'humidite_pourcentage': float(form_data['humidity']),
            'ph_sol': float(form_data['ph']),
            'pluie_mensuelle_mm': float(form_data['Rainfall_Mensuel']),
            'pluie_annuelle_mm': float(form_data['Rainfall_Annuel']),
            
            # Résultats des prédictions ML
            'besoin_irrigation': irrigation_pred,      # "Oui" ou "Non"
            'culture_recommandee': crop_pred,          # "pomme", "banane", etc.
            
            # Métadonnées
            'date_prediction': datetime.utcnow(),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        # Insertion dans MongoDB
        result = predictions_collection.insert_one(prediction_document)
        
        if result.inserted_id:
            print(f"✅ Prédiction sauvegardée pour {current_user.get('email')} - ID: {result.inserted_id}")
            return str(result.inserted_id)
        else:
            print(f"❌ Erreur sauvegarde pour {current_user.get('email')}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur sauvegarde automatique: {e}")
        import traceback
        traceback.print_exc()
        return None

@prediction_bp.route('/complete-prediction', methods=['POST', 'OPTIONS'])
@cross_origin()
@token_required
def complete_prediction_with_save(current_user):
    """
    Endpoint principal : prédiction irrigation + culture + sauvegarde automatique
    """
    try:
        # Gestion des requêtes OPTIONS (CORS preflight)
        if request.method == 'OPTIONS':
            return jsonify({'success': True}), 200
            
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'Aucune donnée fournie'}), 400

        # Validation des champs requis (selon votre formulaire)
        required_fields = ['Nitrogen', 'phosphorous', 'Potassium', 'temperature',
                           'humidity', 'ph', 'Rainfall_Mensuel', 'Rainfall_Annuel']

        missing_fields = [field for field in required_fields if field not in data or str(data[field]).strip() == '']
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Champs manquants ou vides: {", ".join(missing_fields)}'
            }), 400

        # Conversion et validation des données numériques
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
            return jsonify({'success': False, 'error': f'Valeur numérique invalide: {e}'}), 400

        # ---- PRÉDICTION IRRIGATION ----
        irrigation_prediction = "Non déterminée"
        
        if irrigation_model is not None:
            try:
                prediction_result = irrigation_model.predict(input_data)[0]
                # Convertir le résultat numérique en texte
                irrigation_prediction = "Oui" if prediction_result == 0 else "Non"
            except Exception as e:
                print(f"Erreur modèle irrigation, utilisation règles: {e}")
                irrigation_prediction = simulate_irrigation_prediction(data)
        else:
            irrigation_prediction = simulate_irrigation_prediction(data)
        
        # ---- PRÉDICTION CULTURE ----
        crop_recommendation = "Non déterminée"
        
        if crop_model is not None:
            try:
                predicted_crop_index = crop_model.predict(input_data)[0]
                
                if isinstance(predicted_crop_index, (int, np.integer)):
                    if 0 <= predicted_crop_index < len(CROP_CLASSES):
                        crop_recommendation = CROP_CLASSES[predicted_crop_index]
                    else:
                        crop_recommendation = "Index invalide"
                else:
                    crop_recommendation = str(predicted_crop_index).lower()
            except Exception as e:
                print(f"Erreur prédiction culture: {e}")
                crop_recommendation = "Erreur de prédiction"
        else:
            crop_recommendation = "Modèle non disponible"

        # ---- SAUVEGARDE AUTOMATIQUE EN BASE ----
        saved_id = save_prediction_to_db(current_user, data, irrigation_prediction, crop_recommendation)
        
        print(f"🌱 Prédiction complète pour {current_user.get('email')}: Irrigation={irrigation_prediction}, Culture={crop_recommendation}")

        # Réponse JSON complète
        response_data = {
            'success': True,
            'predictions': {
                'irrigation': irrigation_prediction,
                'culture': crop_recommendation
            },
            'user_info': {
                'id': get_user_id_from_current_user(current_user),
                'email': current_user.get('email', ''),
                'nom': current_user.get('nom', current_user.get('name', '')),
                'prenom': current_user.get('prenom', current_user.get('firstname', ''))
            },
            'saved_to_database': saved_id is not None,
            'prediction_id': saved_id,
            'input_parameters': {
                'azote_n': float(data['Nitrogen']),
                'phosphore_p': float(data['phosphorous']),
                'potassium_k': float(data['Potassium']),
                'temperature_celsius': float(data['temperature']),
                'humidite_pourcentage': float(data['humidity']),
                'ph_sol': float(data['ph']),
                'pluie_mensuelle_mm': float(data['Rainfall_Mensuel']),
                'pluie_annuelle_mm': float(data['Rainfall_Annuel'])
            },
            'recommendations': {
                'irrigation_needed': irrigation_prediction,
                'recommended_crop': crop_recommendation,
                'confidence': "Élevée" if irrigation_model and crop_model else "Moyenne"
            },
            'timestamp': datetime.utcnow().isoformat()
        }

        return jsonify(response_data), 200

    except Exception as e:
        print(f"💥 Erreur prédiction complète: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False, 
            'error': 'Erreur serveur lors de la prédiction complète',
            'details': str(e)
        }), 500

@prediction_bp.route('/get-my-predictions', methods=['GET', 'OPTIONS'])
@cross_origin()
@token_required
def get_my_predictions(current_user):
    """
    Récupère toutes les prédictions de l'utilisateur connecté avec pagination
    """
    try:
        if request.method == 'OPTIONS':
            return jsonify({'success': True}), 200
            
        if predictions_collection is None:
            return jsonify({'success': False, 'error': 'Service temporairement indisponible'}), 503
        
        # Paramètres de pagination
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        skip = (page - 1) * limit

        user_id = get_user_id_from_current_user(current_user)

        # Récupération des prédictions avec pagination et tri par date décroissante
        predictions_cursor = predictions_collection.find(
            {'id_agriculteur': user_id}
        ).sort('date_prediction', -1).skip(skip).limit(limit)
        
        predictions = list(predictions_cursor)

        # Comptage total pour la pagination
        total_count = predictions_collection.count_documents({'id_agriculteur': user_id})

        # Conversion des ObjectId et dates en format JSON
        for prediction in predictions:
            prediction['_id'] = str(prediction['_id'])
            if 'date_prediction' in prediction:
                prediction['date_prediction'] = prediction['date_prediction'].isoformat()
            if 'created_at' in prediction:
                prediction['created_at'] = prediction['created_at'].isoformat()
            if 'updated_at' in prediction:
                prediction['updated_at'] = prediction['updated_at'].isoformat()

        return jsonify({
            'success': True,
            'predictions': predictions,
            'pagination': {
                'current_page': page,
                'per_page': limit,
                'total_count': total_count,
                'total_pages': (total_count + limit - 1) // limit,
                'has_next': (skip + limit) < total_count,
                'has_previous': page > 1
            },
            'user': {
                'email': current_user.get('email'),
                'id': user_id
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        print(f"❌ Erreur récupération mes prédictions: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False, 
            'error': 'Erreur lors de la récupération des prédictions',
            'details': str(e)
        }), 500

@prediction_bp.route('/stats/<user_id>', methods=['GET', 'OPTIONS'])
@cross_origin()
@token_required
def get_user_stats(current_user, user_id):
    """
    Statistiques complètes des prédictions d'un utilisateur
    """
    try:
        if request.method == 'OPTIONS':
            return jsonify({'success': True}), 200
            
        if predictions_collection is None:
            return jsonify({'success': False, 'error': 'Service temporairement indisponible'}), 503
        
        current_user_id = get_user_id_from_current_user(current_user)
        
        # Vérification des autorisations (utilisateur ou admin)
        if current_user_id != user_id and current_user.get('role') != 'admin':
            return jsonify({'success': False, 'error': 'Accès non autorisé'}), 403

        # Pipeline d'agrégation MongoDB pour calculer les statistiques
        pipeline = [
            {'$match': {'id_agriculteur': user_id}},
            {
                '$group': {
                    '_id': None,
                    'total_predictions': {'$sum': 1},
                    'irrigation_oui': {
                        '$sum': {
                            '$cond': [{'$eq': ['$besoin_irrigation', 'Oui']}, 1, 0]
                        }
                    },
                    'irrigation_non': {
                        '$sum': {
                            '$cond': [{'$eq': ['$besoin_irrigation', 'Non']}, 1, 0]
                        }
                    },
                    'cultures_uniques': {'$addToSet': '$culture_recommandee'},
                    'avg_temperature': {'$avg': '$temperature_celsius'},
                    'avg_humidity': {'$avg': '$humidite_pourcentage'},
                    'avg_ph': {'$avg': '$ph_sol'},
                    'avg_azote': {'$avg': '$azote_n'},
                    'avg_phosphore': {'$avg': '$phosphore_p'},
                    'avg_potassium': {'$avg': '$potassium_k'},
                    'derniere_prediction': {'$max': '$date_prediction'},
                    'premiere_prediction': {'$min': '$date_prediction'}
                }
            }
        ]

        stats_result = list(predictions_collection.aggregate(pipeline))
        
        # Si aucune prédiction trouvée
        if not stats_result:
            return jsonify({
                'success': True,
                'stats': {
                    'total_predictions': 0,
                    'irrigation': {'oui': 0, 'non': 0, 'pourcentage_oui': 0},
                    'cultures': {'uniques': [], 'nombre_types': 0},
                    'moyennes': {
                        'temperature': 0, 'humidity': 0, 'ph': 0,
                        'azote': 0, 'phosphore': 0, 'potassium': 0
                    },
                    'periode': {'premiere': None, 'derniere': None}
                },
                'user_id': user_id
            }), 200

        stats = stats_result[0]
        total = stats['total_predictions']
        
        response_stats = {
            'success': True,
            'stats': {
                'total_predictions': total,
                'irrigation': {
                    'oui': stats['irrigation_oui'],
                    'non': stats['irrigation_non'],
                    'pourcentage_oui': round((stats['irrigation_oui'] / total * 100) if total > 0 else 0, 1)
                },
                'cultures': {
                    'uniques': stats['cultures_uniques'],
                    'nombre_types': len(stats['cultures_uniques'])
                },
                'moyennes': {
                    'temperature': round(stats.get('avg_temperature', 0), 1),
                    'humidity': round(stats.get('avg_humidity', 0), 1),
                    'ph': round(stats.get('avg_ph', 0), 2),
                    'azote': round(stats.get('avg_azote', 0), 1),
                    'phosphore': round(stats.get('avg_phosphore', 0), 1),
                    'potassium': round(stats.get('avg_potassium', 0), 1)
                },
                'periode': {
                    'premiere': stats['premiere_prediction'].isoformat() if stats.get('premiere_prediction') else None,
                    'derniere': stats['derniere_prediction'].isoformat() if stats.get('derniere_prediction') else None
                }
            },
            'user': {
                'email': current_user.get('email'),
                'id': user_id
            },
            'timestamp': datetime.utcnow().isoformat()
        }

        return jsonify(response_stats), 200

    except Exception as e:
        print(f"❌ Erreur récupération statistiques: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False, 
            'error': 'Erreur lors du calcul des statistiques',
            'details': str(e)
        }), 500

@prediction_bp.route('/delete-prediction/<prediction_id>', methods=['DELETE', 'OPTIONS'])
@cross_origin()
@token_required
def delete_prediction(current_user, prediction_id):
    """
    Supprime une prédiction spécifique de l'utilisateur
    """
    try:
        if request.method == 'OPTIONS':
            return jsonify({'success': True}), 200
            
        if predictions_collection is None:
            return jsonify({'success': False, 'error': 'Service temporairement indisponible'}), 503
           
        # Validation de l'ObjectId MongoDB    
        if not ObjectId.is_valid(prediction_id):
            return jsonify({'success': False, 'error': 'ID de prédiction invalide'}), 400

        user_id = get_user_id_from_current_user(current_user)

        # Vérifier que la prédiction existe et appartient à l'utilisateur
        prediction = predictions_collection.find_one({
            '_id': ObjectId(prediction_id),
            'id_agriculteur': user_id
        })

        if not prediction:
            return jsonify({'success': False, 'error': 'Prédiction non trouvée ou non autorisée'}), 404

        # Suppression de la prédiction
        result = predictions_collection.delete_one({
            '_id': ObjectId(prediction_id),
            'id_agriculteur': user_id
        })

        if result.deleted_count == 1:
            return jsonify({
                'success': True,
                'message': 'Prédiction supprimée avec succès',
                'prediction_id': prediction_id,
                'deleted_data': {
                    'culture': prediction.get('culture_recommandee', ''),
                    'irrigation': prediction.get('besoin_irrigation', ''),
                    'date': prediction.get('date_prediction', '').isoformat() if prediction.get('date_prediction') else ''
                }
            }), 200
        else:
            return jsonify({'success': False, 'error': 'Erreur lors de la suppression'}), 500

    except Exception as e:
        print(f"❌ Erreur suppression prédiction: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False, 
            'error': 'Erreur serveur lors de la suppression',
            'details': str(e)
        }), 500

@prediction_bp.route('/health', methods=['GET'])
@cross_origin()
def prediction_health_check():
    """
    Diagnostic complet du service de prédiction
    """
    try:
        # Test de la base de données
        db_status = "❌ Erreur"
        predictions_count = 0
        try:
            if predictions_collection is not None:
                predictions_count = predictions_collection.count_documents({})
                db_status = "✅ Connecté"
        except Exception as e:
            db_status = f"❌ Erreur: {str(e)}"
        
        # Test des modèles
        irrigation_status = "✅ Chargé" if irrigation_model is not None else "❌ Non chargé"
        crop_status = "✅ Chargé" if crop_model is not None else "❌ Non chargé"
        
        return jsonify({
            'service': 'Prédictions AgriConnect',
            'status': 'healthy' if irrigation_model and crop_model and predictions_collection else 'partial',
            'timestamp': datetime.utcnow().isoformat(),
            'components': {
                'database': {
                    'mongodb_status': db_status,
                    'predictions_collection': predictions_collection is not None,
                    'total_predictions': predictions_count
                },
                'models': {
                    'irrigation_model': irrigation_status,
                    'crop_model': crop_status,
                    'crop_classes_available': len(CROP_CLASSES)
                }
            },
            'endpoints': {
                'POST /complete-prediction': 'Prédiction complète avec sauvegarde',
                'GET /get-my-predictions': 'Historique des prédictions',
                'GET /stats/<user_id>': 'Statistiques utilisateur',
                'DELETE /delete-prediction/<id>': 'Suppression prédiction',
                'GET /health': 'Diagnostic système'
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'service': 'Prédictions AgriConnect',
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500  