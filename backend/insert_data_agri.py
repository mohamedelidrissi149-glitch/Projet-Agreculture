# insert_data_agri.py
from flask import Blueprint, request, jsonify
from flask_cors import CORS, cross_origin
from auth import token_required
from db import Database
from datetime import datetime
import logging 
 
# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint pour l'insertion des données agricoles
insert_agri_bp = Blueprint('insert_agri', __name__, url_prefix='/api')
CORS(insert_agri_bp)

# Instance de la base de données
db = Database()
 
@insert_agri_bp.route('/save-prediction', methods=['POST', 'OPTIONS'])
@cross_origin()
@token_required
def save_agricultural_prediction(current_user):
    """
    Sauvegarde une prédiction agricole dans MongoDB
    """
    try:
        if request.method == 'OPTIONS':
            return jsonify({'success': True}), 200

        # Récupération des données de la requête
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False, 
                'error': 'Aucune donnée fournie'
            }), 400

        # Validation des champs requis
        required_fields = [
            'Nitrogen', 'phosphorous', 'Potassium', 'temperature', 
            'humidity', 'ph', 'Rainfall_Mensuel', 'Rainfall_Annuel',
            'irrigation_prediction', 'crop_recommendation'
        ]
        
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({
                    'success': False, 
                    'error': f'Champ requis manquant: {field}'
                }), 400

        # Accès à la collection predictions
        predictions_collection = db.get_collection('predictions')
        if predictions_collection is None:
            return jsonify({
                'success': False, 
                'error': 'Impossible d\'accéder à la base de données'
            }), 500

        # Préparation du document à insérer
        prediction_document = {
            'id_agriculteur': current_user.get('id'),
            'email_agriculteur': current_user.get('email'),
            'nom_agriculteur': current_user.get('name', ''),
            
            # Données du sol et climatiques
            'azote_n': float(data['Nitrogen']),
            'phosphore_p': float(data['phosphorous']),
            'potassium_k': float(data['Potassium']),
            'temperature_celsius': float(data['temperature']),
            'humidite_pourcentage': float(data['humidity']),
            'ph_sol': float(data['ph']),
            'pluie_mensuelle_mm': float(data['Rainfall_Mensuel']),
            'pluie_annuelle_mm': float(data['Rainfall_Annuel']),
            
            # Résultats des prédictions ML
            'besoin_irrigation': data['irrigation_prediction'],
            'culture_recommandee': data['crop_recommendation'],
            
            # Métadonnées
            'date_prediction': datetime.utcnow(),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        # Insertion dans MongoDB
        result = predictions_collection.insert_one(prediction_document)
        
        if result.inserted_id:
            logger.info(f"Prédiction sauvegardée pour {current_user.get('email')}: {result.inserted_id}")
            
            return jsonify({
                'success': True,
                'message': 'Prédiction sauvegardée avec succès',
                'prediction_id': str(result.inserted_id),
                'user': current_user.get('email'),
                'saved_data': {
                    'irrigation': data['irrigation_prediction'], 
                    'crop': data['crop_recommendation'],
                    'date': prediction_document['date_prediction'].isoformat()
                }
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Échec de la sauvegarde'
            }), 500  

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Erreur de validation des données: {str(e)}'
        }), 400
    except Exception as e:
        logger.error(f"Erreur sauvegarde prédiction: {str(e)}") 
        return jsonify({
            'success': False,
            'error': 'Erreur serveur lors de la sauvegarde'
        }), 500 


@insert_agri_bp.route('/get-user-predictions', methods=['GET', 'OPTIONS'])
@cross_origin()
@token_required
def get_user_predictions(current_user):
    """ 
    Récupère l'historique des prédictions d'un agriculteur
    """
    try:
        if request.method == 'OPTIONS':
            return jsonify({'success': True}), 200

        predictions_collection = db.get_collection('predictions')
        if predictions_collection is None:
            return jsonify({      
                'success': False,   
                'error': 'Impossible d\'accéder à la base de données' 
            }), 500

        # Recherche par email de l'utilisateur connecté
        user_predictions = predictions_collection.find({
            'email_agriculteur': current_user.get('email')
        }).sort('date_prediction', -1)  # Tri par date décroissante

        # Conversion en liste
        predictions_list = []
        for pred in user_predictions:
            predictions_list.append({
                'id': str(pred['_id']),
                'date': pred['date_prediction'].strftime('%Y-%m-%d'),
                'azote': pred['azote_n'],
                'phosphore': pred['phosphore_p'],
                'potassium': pred['potassium_k'],
                'temperature': pred['temperature_celsius'],
                'humidite': pred['humidite_pourcentage'],
                'ph': pred['ph_sol'],
                'pluie_mensuelle': pred['pluie_mensuelle_mm'],
                'pluie_annuelle': pred['pluie_annuelle_mm'],
                'besoin_irrigation': pred['besoin_irrigation'],
                'culture_recommandee': pred['culture_recommandee']
            })

        return jsonify({
            'success': True,
            'predictions': predictions_list,
            'total': len(predictions_list),
            'user': current_user.get('email')
        }), 200

    except Exception as e:
        logger.error(f"Erreur récupération prédictions: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erreur serveur lors de la récupération'
        }), 500


@insert_agri_bp.route('/delete-prediction/<prediction_id>', methods=['DELETE', 'OPTIONS'])
@cross_origin()
@token_required
def delete_prediction(current_user, prediction_id):
    """
    Supprime une prédiction spécifique de l'utilisateur
    """
    try:
        if request.method == 'OPTIONS':
            return jsonify({'success': True}), 200

        from bson import ObjectId
        
        predictions_collection = db.get_collection('predictions')
        if predictions_collection is None:
            return jsonify({
                'success': False, 
                'error': 'Impossible d\'accéder à la base de données'
            }), 500

        # Suppression seulement si c'est la prédiction de l'utilisateur connecté
        result = predictions_collection.delete_one({
            '_id': ObjectId(prediction_id),
            'email_agriculteur': current_user.get('email')
        })

        if result.deleted_count > 0:
            return jsonify({
                'success': True,
                'message': 'Prédiction supprimée avec succès'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Prédiction non trouvée ou non autorisée'
            }), 404

    except Exception as e:
        logger.error(f"Erreur suppression prédiction: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erreur serveur lors de la suppression'
        }), 500   