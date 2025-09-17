from flask import Blueprint, request, jsonify
from db import Database
import jwt
import datetime
from functools import wraps
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

# ----------------- CONFIG -----------------
JWT_SECRET = 'me@fst2021a@'
JWT_ALGORITHM = 'HS256'

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
db = Database()
users_collection = db.get_collection('users')

# ----------------- DÉCORATEURS -----------------
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'success': False, 'message': 'Token manquant'}), 401
        if token.startswith('Bearer '):
            token = token[7:]
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            current_user = users_collection.find_one({'_id': ObjectId(data['user_id'])})
            if not current_user:
                return jsonify({'success': False, 'message': 'Token invalide'}), 401
            current_user['role'] = current_user.get('role', '').strip().lower()
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token expiré'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': 'Token invalide'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Accès admin requis'}), 403
        return f(current_user, *args, **kwargs)
    return token_required(decorated)

# ----------------- ROUTES --------------------------------------------------------------
@auth_bp.route('/login', methods=['POST']) 
def login():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'success': False, 'message': 'Email et mot de passe requis'}), 400

    user = users_collection.find_one({'email': email})
    if not user:
        return jsonify({'success': False, 'message': 'Identifiants incorrects'}), 401

    if not check_password_hash(user['password'], password):
        return jsonify({'success': False, 'message': 'Identifiants incorrects'}), 401

    user_role = user.get('role', '').strip().lower()
    if user_role not in ['admin', 'user']:
        return jsonify({'success': False, 'message': 'Rôle utilisateur non autorisé'}), 403

    payload = {
        'user_id': str(user['_id']),
        'email': user['email'],
        'role': user_role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return jsonify({
        'success': True,
        'token': token,
        'user': {
            'id': str(user['_id']),
            'nom': user.get('nom', ''),
            'prenom': user.get('prenom', ''),
            'email': user['email'],
            'role': user_role
        }
    }), 200

@auth_bp.route('/verify', methods=['GET'])
@token_required
def verify(current_user):
    return jsonify({'success': True, 'user': {
        'id': str(current_user['_id']),
        'nom': current_user.get('nom', ''),
        'prenom': current_user.get('prenom', ''),
        'email': current_user['email'],
        'role': current_user['role']
    }}), 200

@auth_bp.route('/profile', methods=['GET'])
@token_required
def profile(current_user):
    return jsonify({'success': True, 'user': {
        'id': str(current_user['_id']),
        'nom': current_user.get('nom', ''),
        'prenom': current_user.get('prenom', ''),
        'email': current_user['email'],
        'role': current_user['role']
    }}), 200
 