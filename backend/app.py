# app.py
from flask import Flask, jsonify
from flask_cors import CORS
import traceback

# Import des Blueprints
try:
    from register import register_bp
    from auth import auth_bp 
    from clients import clients_bp
    from prediction import prediction_bp      # Version avec sauvegarde (document 22)
    from prompt_gemini import gemini_bp       # Version avec Gemini (document 21) 
    from insert_data_agri import insert_agri_bp
    from get_data_predict import get_data_bp
    print("✅ Tous les blueprints importés avec succès")
except ImportError as e:
    print(f"❌ Erreur d'import blueprint: {e}")
    raise

app = Flask(__name__)
app.url_map.strict_slashes = False

# Configuration CORS simplifiée et efficace
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# ----------------- ENREGISTREMENT DES BLUEPRINTS ----------------------------
try:
    # Register
    app.register_blueprint(register_bp, url_prefix='/api/register')
    print("✅ Blueprint register_bp enregistré")
    
    # Auth
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    print("✅ Blueprint auth_bp enregistré")
    
    # Clients
    app.register_blueprint(clients_bp)  # Supprimez le url_prefix
    print("✅ Blueprint clients_bp enregistré")
         
    # Predictions (AVEC sauvegarde en base) - Document 22
    # Ce blueprint a déjà son préfixe /api dans sa déclaration
    app.register_blueprint(prediction_bp)
    print("✅ Blueprint prediction_bp enregistré (/predict, /crop-recommendation, /save-prediction, /get-user-predictions, /delete-prediction)")
    
    # Gemini conseils - Document 21
    # Ce blueprint n'a PAS de préfixe dans sa déclaration
    app.register_blueprint(gemini_bp, url_prefix='/api')
    print("✅ Blueprint gemini_bp enregistré (/gemini-advice)")
    
    # Autres blueprints si nécessaires
    app.register_blueprint(insert_agri_bp, url_prefix='/api')
    print("✅ Blueprint insert_agri_bp enregistré")
    
    app.register_blueprint(get_data_bp, url_prefix='/api')
    print("✅ Blueprint get_data_bp enregistré")
    
    print("🎯 Tous les blueprints enregistrés avec succès")
    
except Exception as e:
    print(f"❌ Erreur enregistrement blueprint: {e}")
    print(f"❌ Traceback: {traceback.format_exc()}")
    raise

# ----------------- ROUTES PRINCIPALES -------------------------------------------------
@app.route('/')
def home():
    """Page d'accueil de l'API"""
    return jsonify({
        "message": "🚀 API AgriConnect Flask avec MongoDB",
        "status": "✅ Serveur actif",
        "version": "1.0.0",
        "endpoints": {
            "authentication": {
                "register": "/api/register",
                "login": "/api/auth/login",
                "verify": "/api/auth/verify"
            },
            "clients": {
                "list": "/api/clients",
                "create": "/api/clients (POST)",
                "update": "/api/clients/<id> (PUT)",
                "delete": "/api/clients/<id> (DELETE)"
            },
            "predictions": {
                "predict": "/api/predict",
                "crop_recommendation": "/api/crop-recommendation", 
                "save_prediction": "/api/save-prediction",
                "get_user_predictions": "/api/get-user-predictions",
                "delete_prediction": "/api/delete-prediction/<id>",
                "gemini_advice": "/api/gemini-advice"
            },
            "system": {
                "health": "/api/health",
                "test_connection": "/api/test-connection"
            }
        }
    })

@app.route('/api/health')
def health_check():
    """Vérification de l'état de l'API"""
    try:
        from db import Database
        
        db = Database()
        db_status = db.test_connection()
        
        return jsonify({ 
            "status": "OK", 
            "message": "API fonctionne correctement",
            "database": db_status,
            "timestamp": "2025-09-26"
        })
    except Exception as e:
        return jsonify({
            "status": "ERROR",
            "message": f"Erreur health check: {str(e)}",
            "timestamp": "2025-09-26"
        }), 500

@app.route('/api/test-connection')
def test_connection():
    """Test de connexion à MongoDB"""
    try:
        from db import Database
        
        db = Database()
        connection_status = db.test_connection()
        
        if connection_status.get('connected'):
            return jsonify({
                "success": True,
                "message": "Connexion MongoDB réussie",
                "connection": connection_status
            })
        else:
            return jsonify({
                "success": False,
                "message": "Échec connexion MongoDB",
                "connection": connection_status
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Erreur test connexion",
            "error": str(e)
        }), 500

# ----------------- GESTION D'ERREURS -----------------
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Route non trouvée",
        "message": "L'endpoint demandé n'existe pas",
        "available_endpoints": "Consultez / pour la liste complète"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Erreur interne du serveur",
        "message": "Une erreur inattendue s'est produite"
    }), 500

# ----------------- LANCEMENT DU SERVEUR -----------------
if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Démarrage du serveur AgriConnect...")
    print("=" * 60)
    print("📊 Configuration:")
    print(f"   - Host: 0.0.0.0")
    print(f"   - Port: 5000") 
    print(f"   - Mode: Debug")
    print(f"   - CORS: Activé")
    print("=" * 60)
    print("🌐 Endpoints disponibles:")
    print(f"   - API Root: http://localhost:5000/") 
    print(f"   - Health Check: http://localhost:5000/api/health")
    print(f"   - Prédictions: http://localhost:5000/api/predict")
    print(f"   - Cultures: http://localhost:5000/api/crop-recommendation")
    print(f"   - Conseils IA: http://localhost:5000/api/gemini-advice")
    print(f"   - Sauvegarde: http://localhost:5000/api/save-prediction")
    print(f"   - Historique: http://localhost:5000/api/get-user-predictions")
    print("=" * 60)
        
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"❌ Erreur démarrage serveur: {e}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        raise   