# app.py
from flask import Flask, jsonify
from flask_cors import CORS
import numpy as np
  
 
# Import des Blueprints
from register import register_bp
from auth import auth_bp
from clients import clients_bp
from prediction import prediction_bp  # Nouveau Blueprint pour la prédiction

app = Flask(__name__)
CORS(app)

# ----------------- ENREGISTREMENT DES BLUEPRINTS -----------------
app.register_blueprint(register_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(clients_bp) 
app.register_blueprint(prediction_bp)  # Route /api/predict

# ----------------- ROUTES PRINCIPALES ----------------- 
@app.route('/')
def home():
    return jsonify({
        "message": "API Flask avec MongoDB en ligne",
        "endpoints": {
            "clients": "/api/clients",
            "auth": "/api/auth/*",
            "register": "/api/register",
            "predict": "/api/predict"
        }
    })

# Route de test pour vérifier la connexion
@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "OK", 
        "message": "API fonctionne correctement"
    })

# ----------------- LANCEMENT DU SERVEUR -----------------
if __name__ == '__main__':
    print("🚀 Démarrage du serveur AgriConnect...")
    print("🔗 API: http://localhost:5000")
    print("🔗 Frontend: http://localhost:3000")
    app.run(debug=True)  
    