# register.py
from flask import Blueprint, request, jsonify
from flask_cors import CORS, cross_origin
from werkzeug.security import generate_password_hash
from db import Database
import re

register_bp = Blueprint('register', __name__)
CORS(register_bp)

@register_bp.route('', methods=['POST', 'OPTIONS'])
@register_bp.route('/', methods=['POST', 'OPTIONS'])
@cross_origin()
def register():  
    try:
        if request.method == 'OPTIONS':
            return jsonify({'success': True}), 200
  
        data = request.get_json()
        print(f"📝 Données reçues pour inscription: {data}")

        # Champs obligatoires existants
        required_fields = ['nom', 'prenom', 'email', 'ville', 'pays', 'codePostal', 'password']
        for field in required_fields:
            if not data.get(field) or not str(data.get(field)).strip():
                return jsonify({'success': False, 'message': f'Le champ {field} est requis'}), 400

        # Validation email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            return jsonify({'success': False, 'message': 'Format d\'email invalide'}), 400

        # Validation mot de passe
        if len(data['password']) < 6:
            return jsonify({'success': False, 'message': 'Le mot de passe doit contenir au moins 6 caractères'}), 400

        db = Database()
        users_collection = db.get_collection('users')
 
        # Vérifier si l'email existe déjà
        existing_user = users_collection.find_one({'email': data['email'].strip().lower()})
        if existing_user:
            db.close_connection()
            return jsonify({'success': False, 'message': 'Cet email est déjà utilisé'}), 400
                                  
        # Hasher le mot de passe
        hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')

        # Construire l'utilisateur
        new_user = {
            'nom': data['nom'].strip(),
            'prenom': data['prenom'].strip(),
            'email': data['email'].strip().lower(),
            'ville': data['ville'].strip(),
            'pays': data['pays'].strip(),
            'codePostal': data['codePostal'].strip(),
            'password': hashed_password, 
            'role': 'user',  # par défaut
            # ====== NOUVEAUX CHAMPS AJOUTÉS ======
            'dateNaissance': data.get('dateNaissance', ''),
            'genre': data.get('genre', ''),
            'telephone': data.get('telephone', ''),
            'tailleExploitation': data.get('tailleExploitation', ''),
            'canalCommunication': data.get('canalCommunication', ''),
            'languePreferee': data.get('languePreferee', 'francais'),
            'consentementRGPD': data.get('consentementRGPD', False), 
            'validation_du_compte':0 
        } 
                  
        # Insérer le nouvel utilisateur
        result = users_collection.insert_one(new_user)
        user_id = str(result.inserted_id)
        print(f"✅ Utilisateur créé avec ID: {user_id}")

        db.close_connection()
                    
        return jsonify({
            'success': True,
            'message': 'Compte créé avec succès',
            'user': {
                'id': user_id,
                'nom': new_user['nom'],
                'prenom': new_user['prenom'],
                'email': new_user['email'],
                'role': new_user['role']
            }
        }), 201

    except Exception as e:
        print(f"💥 Erreur register: {e}")
        return jsonify({'success': False, 'message': 'Erreur serveur lors de la création du compte'}), 500
      
