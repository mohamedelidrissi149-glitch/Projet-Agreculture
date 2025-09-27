from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from db import Database
import hashlib

# Création du Blueprint
clients_bp = Blueprint('clients', __name__)
print("📋 Blueprint clients créé")

def hash_password(password):
    """Hachage SHA256 d'un mot de passe"""
    return hashlib.sha256(password.encode()).hexdigest()

# ===================== GET ALL CLIENTS =====================
@clients_bp.route('/api/clients', methods=['GET'])
def get_clients():
    print("🔥 ROUTE /api/clients - GET ALL")
    try:
        db = Database()
        result = db.get_all_users()
        
        if not result['success']:
            print(f"❌ Erreur DB: {result['error']}")
            return jsonify({
                "success": False, 
                "message": result['error']
            }), 500
        
        clients = result['users']
        print(f"✅ {len(clients)} clients récupérés")
        
        # Si aucun client, créer des données de test
        if len(clients) == 0:
            print("⚠️ Aucun client - Création de données test")
            test_clients = [
                {
                    "nom": "Dupont", "prenom": "Jean",
                    "email": "jean.dupont@example.com",
                    "ville": "Paris", "pays": "France", "codePostal": "75001"
                },
                {
                    "nom": "Martin", "prenom": "Marie", 
                    "email": "marie.martin@example.com",
                    "ville": "Lyon", "pays": "France", "codePostal": "69001"
                },
                {
                    "nom": "Bernard", "prenom": "Pierre",
                    "email": "pierre.bernard@example.com", 
                    "ville": "Marseille", "pays": "France", "codePostal": "13001"
                }
            ]
            
            # Créer les clients de test
            users_collection = db.get_collection('users')
            if users_collection:
                users_collection.insert_many(test_clients)
                # Récupérer à nouveau
                result = db.get_all_users()
                clients = result['users'] if result['success'] else []
                print(f"✅ {len(clients)} clients test créés")
        
        return jsonify({
            "success": True,
            "clients": clients,
            "total": len(clients)
        }), 200
        
    except Exception as e:
        print(f"💥 ERREUR get_clients: {e}")
        return jsonify({
            "success": False, 
            "message": "Erreur serveur"
        }), 500

# ===================== GET ONE CLIENT =====================
@clients_bp.route('/api/clients/<client_id>', methods=['GET'])
def get_client(client_id):
    print(f"🔥 ROUTE /api/clients/{client_id} - GET ONE")
    try:
        db = Database()
        result = db.get_user_by_id(client_id)
        
        if not result['success']:
            return jsonify({
                "success": False,
                "message": result['error']
            }), 404 if "introuvable" in result['error'] else 500
        
        return jsonify({
            "success": True,
            "client": result['user']
        }), 200
        
    except Exception as e:
        print(f"💥 ERREUR get_client: {e}")
        return jsonify({
            "success": False,
            "message": "Erreur serveur"
        }), 500

# ===================== CREATE CLIENT =====================
@clients_bp.route('/api/clients', methods=['POST'])
def create_client():
    print("🔥 ROUTE /api/clients - CREATE")
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "Données JSON manquantes"
            }), 400
        
        print(f"📝 Données reçues: {data}")
        
        # Préparer les données utilisateur
        user_data = {
            "nom": data.get("nom"),
            "prenom": data.get("prenom"), 
            "email": data.get("email"),
            "ville": data.get("ville"),
            "pays": data.get("pays"),
            "codePostal": data.get("codePostal")
        }
        
        # Ajouter mot de passe si fourni
        if data.get("motDePasse"):
            user_data["motDePasse"] = hash_password(data.get("motDePasse"))
        
        db = Database()
        result = db.create_user(user_data)
        
        if not result['success']:
            return jsonify({
                "success": False,
                "message": result['error']
            }), 400
        
        print(f"✅ Client créé: {result['user_id']}")
        return jsonify({
            "success": True,
            "id": result['user_id'],
            "message": "Client créé avec succès"
        }), 201
        
    except Exception as e:
        print(f"💥 ERREUR create_client: {e}")
        return jsonify({
            "success": False,
            "message": "Erreur serveur"
        }), 500

# ===================== UPDATE CLIENT =====================
@clients_bp.route('/api/clients/<client_id>', methods=['PUT'])
def update_client(client_id):
    print(f"🔥 ROUTE /api/clients/{client_id} - UPDATE")
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "Données JSON manquantes"
            }), 400
        
        # Préparer données de mise à jour
        update_data = {
            "nom": data.get("nom"),
            "prenom": data.get("prenom"),
            "email": data.get("email"), 
            "ville": data.get("ville"),
            "pays": data.get("pays"),
            "codePostal": data.get("codePostal")
        }
        
        # Mot de passe optionnel
        if data.get("motDePasse"):
            update_data["motDePasse"] = hash_password(data.get("motDePasse"))
        
        db = Database()
        result = db.update_user(client_id, update_data)
        
        if not result['success']:
            return jsonify({
                "success": False,
                "message": result['error']
            }), 404 if "introuvable" in result['error'] else 500
        
        print(f"✅ Client {client_id} mis à jour")
        return jsonify({
            "success": True,
            "message": "Client mis à jour avec succès"
        }), 200
        
    except Exception as e:
        print(f"💥 ERREUR update_client: {e}")
        return jsonify({
            "success": False,
            "message": "Erreur serveur"
        }), 500

# ===================== DELETE CLIENT =====================
@clients_bp.route('/api/clients/<client_id>', methods=['DELETE'])
def delete_client(client_id):
    print(f"🔥 ROUTE /api/clients/{client_id} - DELETE")
    try:
        db = Database()
        result = db.delete_user(client_id)
        
        if not result['success']:
            return jsonify({
                "success": False,
                "message": result['error'] 
            }), 404 if "introuvable" in result['error'] else 500
        
        print(f"✅ Client {client_id} supprimé")
        return jsonify({
            "success": True,
            "message": "Client supprimé avec succès"
        }), 200
        
    except Exception as e:
        print(f"💥 ERREUR delete_client: {e}")
        return jsonify({
            "success": False,
            "message": "Erreur serveur" 
        }), 500

# ===================== STATS CLIENTS =====================
@clients_bp.route('/api/clients/stats', methods=['GET'])
def get_clients_stats():
    print("🔥 ROUTE /api/clients/stats - STATS")
    try:
        db = Database()
        result = db.get_user_stats()
        
        if not result['success']:
            return jsonify({
                "success": False,
                "message": result['error']
            }), 500
        
        return jsonify({
            "success": True,
            "stats": result
        }), 200
        
    except Exception as e:
        print(f"💥 ERREUR get_clients_stats: {e}")
        return jsonify({
            "success": False,
            "message": "Erreur serveur"
        }), 500
  
print("✅ Blueprint clients configuré avec 6 routes")      
  