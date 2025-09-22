# insert_prediction.py
from flask import Blueprint, request, jsonify
from auth import token_required
from db import Database
from datetime import datetime
from bson import ObjectId
import traceback

# Création du Blueprint
insert_prediction_bp = Blueprint('insert_prediction', __name__, url_prefix='/api')

# Initialisation de la base de données
db = Database()
predictions_collection = db.get_collection('predictions')

@insert_prediction_bp.route('/save-prediction', methods=['POST'])
@token_required
def save_prediction(current_user):
    """
    Sauvegarde une prédiction dans la collection MongoDB
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Aucune donnée fournie'}), 400

        # Validation des champs requis
        required_fields = [
            'Nitrogen', 'phosphorous', 'Potassium', 'temperature',
            'humidity', 'ph', 'Rainfall_Mensuel', 'Rainfall_Annuel',
            'irrigation_prediction', 'crop_recommendation'
        ]
        
        missing_fields = [field for field in required_fields if field not in data or data[field] == '']
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Champs manquants: {", ".join(missing_fields)}'
            }), 400

        # Création du document à insérer
        prediction_document = {
            'id_agriculteur': current_user['id'],
            'email_agriculteur': current_user['email'],
            'azote_n': float(data['Nitrogen']),
            'phosphore_p': float(data['phosphorous']),
            'potassium_k': float(data['Potassium']),
            'temperature_celsius': float(data['temperature']),
            'humidite_pourcentage': float(data['humidity']),
            'ph_sol': float(data['ph']),
            'pluie_mensuelle_mm': float(data['Rainfall_Mensuel']),
            'pluie_annuelle_mm': float(data['Rainfall_Annuel']),
            'besoin_irrigation': data['irrigation_prediction'],  # "Oui" ou "Non"
            'culture_recommandee': data['crop_recommendation'],  # "pomme", "banane", etc.
            'date_prediction': datetime.utcnow(),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        # Insertion dans MongoDB
        result = predictions_collection.insert_one(prediction_document)
        
        if result.inserted_id:
            print(f"✅ Prédiction sauvegardée pour {current_user['email']} avec ID: {result.inserted_id}")
            
            return jsonify({
                'success': True,
                'message': 'Prédiction sauvegardée avec succès',
                'prediction_id': str(result.inserted_id),
                'user': current_user['email'],
                'data_saved': {
                    'irrigation': data['irrigation_prediction'],
                    'crop': data['crop_recommendation'],
                    'date': datetime.utcnow().isoformat()
                }
            }), 201
        else:
            return jsonify({'success': False, 'error': 'Erreur lors de la sauvegarde'}), 500

    except ValueError as e:
        return jsonify({'success': False, 'error': f'Valeur invalide: {str(e)}'}), 400
    except Exception as e:
        print(f"❌ Erreur sauvegarde prédiction: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Erreur serveur lors de la sauvegarde'}), 500

@insert_prediction_bp.route('/get-predictions/<user_id>', methods=['GET'])
@token_required
def get_user_predictions(current_user, user_id):
    """
    Récupère toutes les prédictions d'un utilisateur
    """
    try:
        # Vérifier que l'utilisateur peut accéder à ses propres données
        if current_user['id'] != user_id and current_user['role'] != 'admin':
            return jsonify({'success': False, 'error': 'Accès non autorisé'}), 403

        # Récupération des prédictions
        predictions = list(predictions_collection.find(
            {'id_agriculteur': user_id}
        ).sort('date_prediction', -1))  # Tri par date décroissante

        # Conversion des ObjectId en strings
        for prediction in predictions:
            prediction['_id'] = str(prediction['_id'])
            prediction['date_prediction'] = prediction['date_prediction'].isoformat()
            if 'created_at' in prediction:
                prediction['created_at'] = prediction['created_at'].isoformat()
            if 'updated_at' in prediction:
                prediction['updated_at'] = prediction['updated_at'].isoformat()

        return jsonify({
            'success': True,
            'predictions': predictions,
            'count': len(predictions),
            'user': current_user['email']
        }), 200

    except Exception as e:
        print(f"❌ Erreur récupération prédictions: {e}")
        return jsonify({'success': False, 'error': 'Erreur lors de la récupération'}), 500

@insert_prediction_bp.route('/get-my-predictions', methods=['GET'])
@token_required
def get_my_predictions(current_user):
    """
    Récupère les prédictions de l'utilisateur connecté
    """
    try:
        # Récupération avec pagination optionnelle
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        skip = (page - 1) * limit

        # Récupération des prédictions avec pagination
        predictions = list(predictions_collection.find(
            {'id_agriculteur': current_user['id']}
        ).sort('date_prediction', -1).skip(skip).limit(limit))

        # Comptage total
        total_count = predictions_collection.count_documents({'id_agriculteur': current_user['id']})

        # Conversion des ObjectId en strings
        for prediction in predictions:
            prediction['_id'] = str(prediction['_id'])
            prediction['date_prediction'] = prediction['date_prediction'].isoformat()

        return jsonify({
            'success': True,
            'predictions': predictions,
            'count': len(predictions),
            'total_count': total_count,
            'page': page,
            'total_pages': (total_count + limit - 1) // limit,
            'user': current_user['email']
        }), 200

    except Exception as e:
        print(f"❌ Erreur récupération mes prédictions: {e}")
        return jsonify({'success': False, 'error': 'Erreur lors de la récupération'}), 500

@insert_prediction_bp.route('/stats/<user_id>', methods=['GET'])
@token_required
def get_user_stats(current_user, user_id):
    """
    Statistiques des prédictions d'un utilisateur
    """
    try:
        # Vérification des autorisations
        if current_user['id'] != user_id and current_user['role'] != 'admin':
            return jsonify({'success': False, 'error': 'Accès non autorisé'}), 403

        # Agrégation des statistiques
        pipeline = [
            {'$match': {'id_agriculteur': user_id}},
            {
                '$group': {
                    '_id': None,
                    'total_predictions': {'$sum': 1},
                    'irrigation_oui': {
                        '$sum': {
                            '$cond': [{'$regexMatch': {'input': '$besoin_irrigation', 'regex': 'Oui'}}, 1, 0]
                        }
                    },
                    'irrigation_non': {
                        '$sum': {
                            '$cond': [{'$regexMatch': {'input': '$besoin_irrigation', 'regex': 'Non'}}, 1, 0]
                        }
                    },
                    'cultures': {'$addToSet': '$culture_recommandee'},
                    'avg_temperature': {'$avg': '$temperature_celsius'},
                    'avg_humidity': {'$avg': '$humidite_pourcentage'},
                    'avg_ph': {'$avg': '$ph_sol'},
                    'derniere_prediction': {'$max': '$date_prediction'}
                }
            }
        ]

        stats_result = list(predictions_collection.aggregate(pipeline))
        
        if not stats_result:
            return jsonify({
                'success': True,
                'stats': {
                    'total_predictions': 0,
                    'irrigation_oui': 0,
                    'irrigation_non': 0,
                    'pourcentage_irrigation': 0,
                    'cultures_uniques': [],
                    'moyennes': {
                        'temperature': 0,
                        'humidity': 0,
                        'ph': 0
                    }
                }
            }), 200

        stats = stats_result[0]
        total = stats['total_predictions']
        
        return jsonify({
            'success': True,
            'stats': {
                'total_predictions': total,
                'irrigation_oui': stats['irrigation_oui'],
                'irrigation_non': stats['irrigation_non'],
                'pourcentage_irrigation': round((stats['irrigation_oui'] / total * 100) if total > 0 else 0, 1),
                'cultures_uniques': stats['cultures'],
                'nombre_cultures_differentes': len(stats['cultures']),
                'moyennes': {
                    'temperature': round(stats.get('avg_temperature', 0), 1),
                    'humidity': round(stats.get('avg_humidity', 0), 1),
                    'ph': round(stats.get('avg_ph', 0), 2)
                },
                'derniere_prediction': stats['derniere_prediction'].isoformat() if stats.get('derniere_prediction') else None
            },
            'user': current_user['email']
        }), 200

    except Exception as e:
        print(f"❌ Erreur récupération statistiques: {e}")
        return jsonify({'success': False, 'error': 'Erreur lors du calcul des statistiques'}), 500

@insert_prediction_bp.route('/delete-prediction/<prediction_id>', methods=['DELETE'])
@token_required
def delete_prediction(current_user, prediction_id):
    """
    Supprime une prédiction spécifique
    """
    try:
        # Validation de l'ObjectId
        if not ObjectId.is_valid(prediction_id):
            return jsonify({'success': False, 'error': 'ID de prédiction invalide'}), 400

        # Vérifier que la prédiction appartient à l'utilisateur
        prediction = predictions_collection.find_one({
            '_id': ObjectId(prediction_id),
            'id_agriculteur': current_user['id']
        })

        if not prediction:
            return jsonify({'success': False, 'error': 'Prédiction non trouvée ou non autorisée'}), 404

        # Suppression
        result = predictions_collection.delete_one({'_id': ObjectId(prediction_id)})

        if result.deleted_count == 1:
            return jsonify({
                'success': True,
                'message': 'Prédiction supprimée avec succès',
                'prediction_id': prediction_id
            }), 200
        else:
            return jsonify({'success': False, 'error': 'Erreur lors de la suppression'}), 500

    except Exception as e:
        print(f"❌ Erreur suppression prédiction: {e}")
        return jsonify({'success': False, 'error': 'Erreur serveur lors de la suppression'}), 500

@insert_prediction_bp.route('/predictions-health', methods=['GET'])
def predictions_health():
    """
    Vérification de la santé de la collection predictions
    """
    try:
        # Comptage des documents
        total_predictions = predictions_collection.count_documents({})
        
        # Dernière prédiction
        latest_prediction = predictions_collection.find_one(
            {}, sort=[('date_prediction', -1)]
        )
        
        return jsonify({
            'status': 'healthy',
            'collection': 'predictions',
            'total_documents': total_predictions,
            'latest_prediction': latest_prediction['date_prediction'].isoformat() if latest_prediction else None,
            'database_connection': True
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'database_connection': False
        }), 500  