from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from db import Database

clients_bp = Blueprint('clients', __name__)

# ------------------ GET ALL CLIENTS ------------------
@clients_bp.route('/api/clients', methods=['GET'])
def get_clients():
    try:
        db = Database()
        users_collection = db.get_collection('users')

        clients = list(users_collection.find({}, {
            "_id": 1, "nom": 1, "prenom": 1, "email": 1,
            "ville": 1, "pays": 1, "codePostal": 1
        }))

        for client in clients:
            client["id"] = str(client["_id"])
            del client["_id"]

        db.close_connection()
        return jsonify({"success": True, "clients": clients}), 200

    except Exception as e:
        print(f"💥 Erreur get_clients: {e}")
        return jsonify({"success": False, "message": "Erreur serveur"}), 500


# ------------------ GET ONE CLIENT ------------------
@clients_bp.route('/api/clients/<id>', methods=['GET'])
def get_client(id):
    try:
        db = Database()
        users_collection = db.get_collection('users')

        client = users_collection.find_one({"_id": ObjectId(id)})
        db.close_connection()

        if not client:
            return jsonify({"success": False, "message": "Client introuvable"}), 404

        client["id"] = str(client["_id"])
        del client["_id"]

        return jsonify({"success": True, "client": client}), 200

    except Exception as e:
        print(f"💥 Erreur get_client: {e}")
        return jsonify({"success": False, "message": "Erreur serveur"}), 500


# ------------------ CREATE CLIENT ------------------
@clients_bp.route('/api/clients', methods=['POST'])
def create_client():
    try:
        data = request.json
        db = Database()
        users_collection = db.get_collection('users')

        new_client = {
            "nom": data.get("nom"),
            "prenom": data.get("prenom"),
            "email": data.get("email"),
            "ville": data.get("ville"),
            "pays": data.get("pays"),
            "codePostal": data.get("codePostal"),
        }

        result = users_collection.insert_one(new_client)
        db.close_connection()

        return jsonify({"success": True, "id": str(result.inserted_id)}), 201

    except Exception as e:
        print(f"💥 Erreur create_client: {e}")
        return jsonify({"success": False, "message": "Erreur serveur"}), 500


# ------------------ UPDATE CLIENT ------------------
@clients_bp.route('/api/clients/<id>', methods=['PUT'])
def update_client(id):
    try:
        data = request.json
        db = Database()
        users_collection = db.get_collection('users')

        update_data = {
            "nom": data.get("nom"),
            "prenom": data.get("prenom"),
            "email": data.get("email"),
            "ville": data.get("ville"),
            "pays": data.get("pays"),
            "codePostal": data.get("codePostal"),
        }

        result = users_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": update_data}
        )

        db.close_connection()

        if result.matched_count == 0:
            return jsonify({"success": False, "message": "Client introuvable"}), 404

        return jsonify({"success": True, "message": "Client mis à jour"}), 200

    except Exception as e:
        print(f"💥 Erreur update_client: {e}")
        return jsonify({"success": False, "message": "Erreur serveur"}), 500


# ------------------ DELETE CLIENT ------------------
@clients_bp.route('/api/clients/<id>', methods=['DELETE'])
def delete_client(id):
    try:
        db = Database()
        users_collection = db.get_collection('users')

        result = users_collection.delete_one({"_id": ObjectId(id)})
        db.close_connection()

        if result.deleted_count == 0:
            return jsonify({"success": False, "message": "Client introuvable"}), 404

        return jsonify({"success": True, "message": "Client supprimé"}), 200

    except Exception as e:
        print(f"💥 Erreur delete_client: {e}")
        return jsonify({"success": False, "message": "Erreur serveur"}), 500
 