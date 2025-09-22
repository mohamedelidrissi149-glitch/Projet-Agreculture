# app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timezone
import traceback

# Pour la sérialisation Mongo
from bson import ObjectId
from datetime import datetime as dt

# Import dynamique de Database (ton module db.py)
# On suppose que db.Database existe et fournit get_collection(name)
try:
    from db import Database
except Exception:
    Database = None  # on gérera le fallback plus bas

app = Flask(__name__)
CORS(app)

# Configuration de l'application
app.config['SECRET_KEY'] = 'me@fst2021a@'
app.config['MONGODB_URI'] = 'mongodb://localhost:27017/'
app.config['DATABASE_NAME'] = 'basejwt'

# ----------------- IMPORT & ENREGISTREMENT DES BLUEPRINTS -----------------
# On essaye d'importer les blueprints mais si l'un manque on continue et on log.
blueprints = [
    ('register', 'register_bp'),
    ('auth', 'auth_bp'),
    ('clients', 'clients_bp'),
    ('prediction', 'prediction_bp'),
]

for module_name, bp_name in blueprints:
    try:
        module = __import__(module_name)
        bp = getattr(module, bp_name)
        # Par défaut, on les expose sous /api/<module_name> (optionnel)
        app.register_blueprint(bp, url_prefix='/api')
        print(f"✅ Blueprint '{module_name}' chargé et enregistré.")
    except Exception as e:
        print(f"⚠️  Impossible de charger le blueprint '{module_name}': {e}")

# ----------------- UTILITAIRES -----------------
def get_db():
    """
    Retourne une instance de connexion à la DB utilisant db.Database si disponible.
    Si Database n'existe pas, on renvoie None (l'appelant gérera).
    """
    if Database is None:
        return None
    try:
        return Database()
    except Exception as e:
        print(f"Erreur initialisation Database(): {e}")
        return None

def serialize_mongo_doc(doc: dict) -> dict:
    """Convertit ObjectId et datetimes en types JSON-serializables."""
    result = {}
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            result[k] = str(v)
        elif isinstance(v, dt):
            # isoformat en UTC si possible
            if v.tzinfo is None:
                result[k] = v.replace(tzinfo=timezone.utc).isoformat()
            else:
                result[k] = v.isoformat()
        else:
            # si c'est un dict imbriqué, on essaie de sérialiser récursivement
            if isinstance(v, dict):
                result[k] = serialize_mongo_doc(v)
            else:
                result[k] = v
    return result

# ----------------- ROUTES PRINCIPALES -----------------
@app.route('/')
def home():
    return jsonify({
        "message": "API AgriConnect - Système de prédiction agricole avec IA",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "Authentification JWT",
            "Prédiction d'irrigation ML",
            "Recommandation de cultures ML",
            "Sauvegarde automatique MongoDB",
            "Historique et statistiques"
        ],
        "endpoints": {
            "auth": {
                "login": "/api/auth/login",
                "verify": "/api/auth/verify",
                "profile": "/api/auth/profile"
            },
            "predictions": {
                "complete": "/api/complete-prediction",
                "history": "/api/get-my-predictions",
                "stats": "/api/stats/<user_id>",
                "delete": "/api/delete-prediction/<prediction_id>"
            },
            "admin": {
                "clients": "/api/clients",
                "health": "/api/health"
            }
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "OK",
        "message": "API AgriConnect fonctionne correctement",
        "services": {
            "flask": "active",
            # On ne peut pas garantir la connexion Mongo ici sans l'ouvrir; tentative simple:
            "mongodb": "connected" if get_db() is not None else "not_initialized",
            "ml_models": "loaded",  # changer si tu veux vérifier réellement
            "auth_system": "active"
        },
        "timestamp": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    })

# ----------------- STATISTIQUES SYSTÈME -----------------
@app.route('/api/system-stats', methods=['GET'])
def system_stats():
    """
    Retourne des statistiques générales:
    - total_users
    - total_predictions
    - recent_predictions (dernières 5)
    """
    try:
        db = get_db()
        if db is None:
            # Pas de Database configurée => retourner message clair
            return jsonify({
                "success": False,
                "error": "Database non initialisée. Vérifiez le module 'db.py' et la configuration."
            }), 500

        users_collection = None
        predictions_collection = None

        try:
            users_collection = db.get_collection('users')
        except Exception:
            users_collection = None

        try:
            predictions_collection = db.get_collection('predictions')
        except Exception:
            predictions_collection = None

        total_users = users_collection.count_documents({}) if users_collection is not None else 0
        total_predictions = predictions_collection.count_documents({}) if predictions_collection is not None else 0

        recent_predictions = []
        if predictions_collection is not None:
            cursor = predictions_collection.find(
                {},
                {'email_agriculteur': 1, 'date_prediction': 1, 'culture_recommandee': 1}
            ).sort('date_prediction', -1).limit(5)
            for p in cursor:
                recent_predictions.append(serialize_mongo_doc(p))

        return jsonify({
            "success": True,
            "stats": {
                "total_users": total_users,
                "total_predictions": total_predictions,
                "recent_predictions": recent_predictions
            },
            "timestamp": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
        })

    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Erreur system_stats:", traceback_str)
        return jsonify({
            "success": False,
            "error": f"Erreur récupération statistiques: {str(e)}"
        }), 500

# ----------------- GESTIONNAIRES D'ERREURS -----------------
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint non trouvé',
        'message': 'Vérifiez l\'URL et la méthode HTTP',
        'available_endpoints': '/'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Erreur serveur interne',
        'message': 'Une erreur inattendue s\'est produite'
    }), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'error': 'Requête invalide',
        'message': 'Vérifiez les paramètres de votre requête'
    }), 400

# ----------------- MIDDLEWARE / LOG -----------------
@app.before_request
def log_request_info():
    print(f"🌐 {datetime.utcnow().isoformat()} - {request.method} {request.path}")

# ----------------- LANCEMENT DU SERVEUR -----------------
if __name__ == '__main__':
    print("🚀 Démarrage du serveur AgriConnect...")
    print("=" * 60)
    print("🔗 API principale: http://localhost:5000")
    print("🔗 Documentation: http://localhost:5000/")
    print("🔗 Frontend React: http://localhost:3000")
    print("=" * 60)
    print("📊 Services disponibles:")
    print("   - Authentification JWT (existant)")
    print("   - Prédiction irrigation ML")
    print("   - Recommandation cultures ML")
    print("   - Sauvegarde MongoDB automatique")
    print("   - Historique et statistiques utilisateur")
    print("=" * 60)
    print("🎯 Endpoints principaux:")
    print("   - POST /api/auth/login (authentification)")
    print("   - POST /api/complete-prediction (prédiction complète)")
    print("   - GET  /api/get-my-predictions (historique)")
    print("   - GET  /api/stats/<user_id> (statistiques)")
    print("   - DELETE /api/delete-prediction/<id> (supprimer)")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)
  