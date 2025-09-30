# CreationAccountAgriculteur.py - Version USER FORCÉ - 100% GARANTIE
from flask import Blueprint, request, jsonify
from flask_cors import CORS, cross_origin
from werkzeug.security import generate_password_hash
from db import Database
import jwt
import re
import traceback
from datetime import datetime
from bson.objectid import ObjectId

# Création du Blueprint
admin_agriculteur_bp = Blueprint('admin_agriculteur', __name__)
CORS(admin_agriculteur_bp)

# MÊME CLÉ JWT QUE auth.py - CRITIQUE
JWT_SECRET = 'me@fst2021a@'

def verify_admin_token(token):
    """Vérifier le token admin avec logs détaillés"""
    try:
        print("="*60)
        print("🔍 DÉBUT VÉRIFICATION TOKEN ADMIN")
        print("="*60)
        
        if not token:
            print("❌ ERREUR: Aucun token fourni")
            return None
            
        # Nettoyer le token
        original_token = token
        if token.startswith('Bearer '):
            token = token[7:]
            
        print(f"📋 Token original: {original_token[:50]}...")
        print(f"📋 Token nettoyé: {token[:50]}...")
        print(f"🔑 Secret JWT: {JWT_SECRET}")
        
        # Décoder sans vérification pour debug
        try:
            payload_non_verifie = jwt.decode(token, options={"verify_signature": False})
            print(f"📊 Contenu token (non vérifié): {payload_non_verifie}")
        except Exception as e:
            print(f"⚠️ Erreur lecture token: {e}")
        
        # Décoder avec vérification
        print("🔄 Décodage avec vérification...")
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        print(f"✅ SUCCÈS décodage token!")
        print(f"   - User ID: {payload.get('user_id')}")
        print(f"   - Email: {payload.get('email')}")  
        print(f"   - Rôle: {payload.get('role')}")
        
        # Vérifier le rôle admin
        if payload.get('role') == 'admin':
            print("✅ Rôle admin confirmé dans le token")
            
            # Vérification en base
            print("🔍 Vérification utilisateur en base...")
            db = Database()
            users_collection = db.get_collection('users')
            
            try:
                user_id = payload.get('user_id')
                user = users_collection.find_one({'_id': ObjectId(user_id)})
                
                if user:
                    print(f"✅ Utilisateur trouvé:")
                    print(f"   - Email: {user.get('email')}")
                    print(f"   - Rôle en base: {user.get('role')}")
                    
                    if user.get('role') == 'admin':
                        print("🎉 SUCCÈS TOTAL - Admin vérifié")
                        db.close_connection()
                        print("="*60)
                        return user
                    else:
                        print(f"❌ Rôle en base incorrect: {user.get('role')}")
                else:
                    print("❌ Utilisateur non trouvé en base")
                    
                db.close_connection()
                
            except Exception as db_e:
                print(f"❌ Erreur base: {db_e}")
                db.close_connection()
        else:
            print(f"❌ Rôle incorrect: '{payload.get('role')}' (attendu: admin)")
            
        print("="*60)
        return None
        
    except jwt.ExpiredSignatureError:
        print("❌ Token expiré")
        return None
    except jwt.InvalidTokenError as e:
        print(f"❌ Token invalide: {e}")
        return None
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return None

@admin_agriculteur_bp.route('/admin/create-agriculteur', methods=['POST', 'OPTIONS'])
@cross_origin()
def create_agriculteur():
    """Créer un compte utilisateur (jamais agriculteur)"""
    try:
        if request.method == 'OPTIONS':
            response = jsonify({'success': True})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
            return response, 200

        print("\n" + "="*70)
        print("🚜 CRÉATION COMPTE UTILISATEUR - DÉBUT")
        print("="*70)
        
        # Vérification token
        auth_header = request.headers.get('Authorization')
        print(f"🔐 Header Authorization: {'✅ Présent' if auth_header else '❌ Manquant'}")
        
        if not auth_header:
            return jsonify({
                'success': False, 
                'message': 'Token d\'autorisation manquant'
            }), 401
            
        admin_user = verify_admin_token(auth_header)
        
        if not admin_user:
            print("❌ ÉCHEC vérification admin")
            return jsonify({
                'success': False, 
                'message': 'Accès refusé. Seuls les administrateurs peuvent créer des comptes utilisateurs.'
            }), 403

        print(f"🎉 Admin authentifié: {admin_user.get('email')}")

        # Récupération données
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Aucune donnée reçue'}), 400
            
        print(f"📧 Email utilisateur: {data.get('email')}")

        # Validations
        required_fields = ['nom', 'prenom', 'email', 'ville', 'pays', 'codePostal', 'password']
        for field in required_fields:
            if not data.get(field) or not str(data.get(field)).strip():
                return jsonify({'success': False, 'message': f'Le champ {field} est requis'}), 400

        required_user_fields = ['dateNaissance', 'genre', 'telephone', 'tailleExploitation', 'canalCommunication']
        for field in required_user_fields:
            if not data.get(field) or not str(data.get(field)).strip():
                return jsonify({'success': False, 'message': f'Le champ {field} est requis'}), 400

        if not data.get('consentementRGPD'):
            return jsonify({'success': False, 'message': 'Consentement RGPD requis'}), 400

        # Validation email
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data['email']):
            return jsonify({'success': False, 'message': 'Format email invalide'}), 400

        # Validation mot de passe
        if len(data['password']) < 6:
            return jsonify({'success': False, 'message': 'Mot de passe trop court (min 6 caractères)'}), 400

        # Validation date
        try:
            birth_date = datetime.strptime(data['dateNaissance'], '%Y-%m-%d')
            age = (datetime.now() - birth_date).days / 365.25
            if age < 16 or age > 100:
                return jsonify({'success': False, 'message': 'Âge invalide (16-100 ans)'}), 400
        except ValueError:
            return jsonify({'success': False, 'message': 'Format date invalide'}), 400

        print("✅ Toutes les validations passées")

        # Base de données
        db = Database()
        users_collection = db.get_collection('users')

        # Vérifier email unique
        if users_collection.find_one({'email': data['email'].strip().lower()}):
            db.close_connection()
            return jsonify({'success': False, 'message': 'Email déjà utilisé'}), 400

        # Hasher mot de passe
        hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')

        # =====================================================================
        # ATTENTION: TOUS LES COMPTES CRÉÉS AURONT TOUJOURS LE RÔLE "user"
        # =====================================================================
        
        # Créer utilisateur - RÔLE FORCÉ À "user"
        new_user = {
            # Données de base
            'nom': data['nom'].strip(),
            'prenom': data['prenom'].strip(),
            'email': data['email'].strip().lower(),
            'ville': data['ville'].strip(),
            'pays': data['pays'].strip(),
            'codePostal': data['codePostal'].strip(),
            'password': hashed_password,
            
            # =====================================================================
            # RÔLE FORCÉ À "user" - NE JAMAIS CHANGER CETTE LIGNE
            # =====================================================================
            'role': 'user',  # ⚠️ TOUJOURS "user" - JAMAIS "agriculteur"
            
            # Données personnelles
            'dateNaissance': data['dateNaissance'],
            'genre': data['genre'],
            'telephone': data['telephone'].strip(),
            
            # Exploitation
            'tailleExploitation': data['tailleExploitation'],
            'canalCommunication': data['canalCommunication'],
            'languePreferee': data.get('languePreferee', 'francais'),
            'consentementRGPD': True,
            
            # Métadonnées - TOUTES RÉFÉRENCES À "user"
            'validation_du_compte': 1,
            'created_by_admin': admin_user['email'],
            'creation_date': datetime.utcnow(),
            'account_type': 'user',  # ⚠️ TOUJOURS "user" - JAMAIS "agriculteur"
            'account_status': 'active',
            'email_verified': True,
            'profile_completed': True,
            'first_login': True,
            'last_activity': datetime.utcnow()
        }

        # VÉRIFICATION DE SÉCURITÉ - S'assurer que le rôle est "user"
        if new_user['role'] != 'user':
            print("🚨 ALERTE SÉCURITÉ: Tentative de création avec rôle non-user")
            new_user['role'] = 'user'  # Force le rôle à user
            
        if new_user['account_type'] != 'user':
            print("🚨 ALERTE SÉCURITÉ: Tentative de création avec account_type non-user")
            new_user['account_type'] = 'user'  # Force l'account_type à user

        # LOG DE VÉRIFICATION FINALE
        print("🔍 VÉRIFICATION FINALE DES DONNÉES:")
        print(f"   - Rôle: '{new_user['role']}' (doit être 'user')")
        print(f"   - Type compte: '{new_user['account_type']}' (doit être 'user')")
        
        # Double vérification avant insertion
        assert new_user['role'] == 'user', "ERREUR: Le rôle n'est pas 'user'"
        assert new_user['account_type'] == 'user', "ERREUR: Le type de compte n'est pas 'user'"

        # Insertion
        result = users_collection.insert_one(new_user)
        user_id = str(result.inserted_id)
        
        # VÉRIFICATION POST-INSERTION
        inserted_user = users_collection.find_one({'_id': result.inserted_id})
        if inserted_user and inserted_user.get('role') != 'user':
            print("🚨 ERREUR CRITIQUE: Le rôle en base n'est pas 'user' !")
            # Corriger immédiatement
            users_collection.update_one(
                {'_id': result.inserted_id}, 
                {'$set': {'role': 'user', 'account_type': 'user'}}
            )
            print("✅ CORRECTION APPLIQUÉE: Rôle forcé à 'user'")
        
        print(f"🎉 SUCCÈS - Utilisateur créé:")
        print(f"   - ID: {user_id}")
        print(f"   - Email: {new_user['email']}")
        print(f"   - Nom: {new_user['prenom']} {new_user['nom']}")
        print(f"   - Rôle: {new_user['role']} (GARANTI 'user')")
        print(f"   - Type: {new_user['account_type']} (GARANTI 'user')")

        db.close_connection()

        print("="*70)
        print("🎉 CRÉATION RÉUSSIE - RÔLE USER GARANTI")
        print("="*70)

        # Réponse succès
        return jsonify({
            'success': True,
            'message': 'Compte utilisateur créé avec succès',
            'user': {
                'id': user_id,
                'nom': new_user['nom'],
                'prenom': new_user['prenom'],
                'email': new_user['email'],
                'role': 'user',  # ⚠️ TOUJOURS "user" dans la réponse
                'pays': new_user['pays'],
                'ville': new_user['ville'],
                'account_type': 'user',  # ⚠️ TOUJOURS "user" dans la réponse
                'creation_date': new_user['creation_date'].isoformat()
            }
        }), 201

    except Exception as e:
        print(f"💥 ERREUR FATALE: {e}")
        print(f"💥 Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False, 
            'message': 'Erreur serveur',
            'error': str(e)
        }), 500

# Route de diagnostic
@admin_agriculteur_bp.route('/admin/verify-token', methods=['GET', 'POST'])
@cross_origin()
def verify_token_debug():
    """Diagnostic token"""
    auth_header = request.headers.get('Authorization')
    print(f"🔍 DIAGNOSTIC - Token: {auth_header[:50] if auth_header else 'Aucun'}...")
    
    if not auth_header:
        return jsonify({'success': False, 'message': 'Pas de token'}), 401
        
    admin_user = verify_admin_token(auth_header)
    
    if admin_user:
        return jsonify({
            'success': True,
            'message': 'Token valide',
            'admin_info': {
                'id': str(admin_user['_id']),
                'email': admin_user.get('email'),
                'role': admin_user.get('role')
            }
        }), 200
    else:
        return jsonify({'success': False, 'message': 'Token invalide'}), 403

@admin_agriculteur_bp.route('/admin/test', methods=['GET'])
def test_admin_blueprint():
    """Test du blueprint"""
    return jsonify({
        'success': True,
        'message': 'Blueprint fonctionne - TOUS les comptes créés avec rôle USER GARANTI',
        'role_policy': 'FORCED_USER_ROLE',
        'timestamp': datetime.utcnow().isoformat()
    })

# Route pour corriger les anciens comptes
@admin_agriculteur_bp.route('/admin/fix-roles', methods=['POST'])
@cross_origin()
def fix_existing_roles():
    """Corriger tous les comptes avec rôle 'agriculteur' vers 'user'"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'success': False, 'message': 'Token manquant'}), 401
            
        admin_user = verify_admin_token(auth_header)
        if not admin_user:
            return jsonify({'success': False, 'message': 'Accès refusé'}), 403

        print("🔧 CORRECTION DES RÔLES EXISTANTS")
        
        db = Database()
        users_collection = db.get_collection('users')
        
        # Trouver tous les comptes avec rôle "agriculteur"
        agriculteurs = list(users_collection.find({'role': 'agriculteur'}))
        print(f"📊 Trouvé {len(agriculteurs)} comptes avec rôle 'agriculteur'")
        
        if len(agriculteurs) == 0:
            db.close_connection()
            return jsonify({
                'success': True,
                'message': 'Aucun compte à corriger',
                'corrected_count': 0
            })
        
        # Corriger tous les comptes
        result = users_collection.update_many(
            {'role': 'agriculteur'}, 
            {
                '$set': {
                    'role': 'user',
                    'account_type': 'user',
                    'role_corrected_date': datetime.utcnow(),
                    'corrected_by_admin': admin_user['email']
                }
            }
        )
        
        print(f"✅ {result.modified_count} comptes corrigés")
        
        db.close_connection()
        
        return jsonify({
            'success': True,
            'message': f'{result.modified_count} comptes corrigés vers le rôle "user"',
            'corrected_count': result.modified_count
        })
        
    except Exception as e:
        print(f"❌ Erreur correction rôles: {e}")
        return jsonify({
            'success': False,
            'message': 'Erreur lors de la correction',
            'error': str(e)
        }), 500  