# get_data_predict.py
from flask import Blueprint, jsonify, request
from db import Database
from datetime import datetime
import traceback

get_data_bp = Blueprint('get_data_bp', __name__)

def get_predictions_collection():
    """Récupère la collection predictions avec gestion d'erreur"""
    try:
        print("🔄 Initialisation connexion Database...")
        db = Database()
        
        if db.client is None or db.db is None:
            print("❌ Erreur: Database non initialisée")
            return None
            
        collection = db.get_collection('predictions')
        if collection is None:
            print("❌ Erreur: Collection predictions inaccessible")
            return None
            
        print("✅ Collection predictions accessible")
        return collection
    except Exception as e:
        print(f"❌ Erreur accès collection: {e}")
        traceback.print_exc()
        return None

def serialize_doc(doc):
    """Sérialise un document MongoDB en format JSON"""
    try:
        if not doc:
            return None
            
        # Affichage du document pour debug
        print(f"🔍 Sérialisation document: {doc.get('email_agriculteur', 'N/A')}")
        
        return {
            "email_agriculteur": doc.get("email_agriculteur", "-"),
            "nom_agriculteur": doc.get("nom_agriculteur", "-"),
            "azote": doc.get("azote_n", 0),
            "phosphore": doc.get("phosphore_p", 0),
            "potassium": doc.get("potassium_k", 0),
            "temperature_celsius": doc.get("temperature_celsius", 0),
            "humidite_pourcentage": doc.get("humidite_pourcentage", 0),
            "ph": doc.get("ph_sol", 0),
            "pluie_mensuelle_mm": doc.get("pluie_mensuelle_mm", 0),
            "pluie_annuelle_mm": doc.get("pluie_annuelle_mm", 0),
            "besoin_irrigation": doc.get("besoin_irrigation", "-"),
            "culture_recommandee": doc.get("culture_recommandee", "-"),
            "date_prediction": doc.get("date_prediction").isoformat() if doc.get("date_prediction") else datetime.now().isoformat(),
            # Champs pour suppression
            "azote_n": doc.get("azote_n", 0),
            "phosphore_p": doc.get("phosphore_p", 0),
        }
    except Exception as e:
        print(f"❌ Erreur sérialisation: {e}")
        return None

@get_data_bp.route('/predictions', methods=['GET'])
def get_predictions():
    """Récupère toutes les prédictions"""
    try:
        print("🚀 === DÉBUT GET_PREDICTIONS ===")
        
        collection = get_predictions_collection()
        if collection is None:
            print("❌ Collection inaccessible")
            return jsonify({
                "success": False,
                "error": "Collection predictions inaccessible",
                "data": []
            }), 500

        # Vérification que la collection contient des données
        try:
            total_count = collection.count_documents({})
            print(f"📊 Total documents dans collection: {total_count}")
            
            if total_count == 0:
                print("⚠️ Aucun document dans la collection")
                return jsonify({
                    "success": True,
                    "data": [],
                    "total": 0,
                    "message": "Aucune prédiction trouvée"
                })
                
        except Exception as e:
            print(f"❌ Erreur count documents: {e}")
            return jsonify({
                "success": False,
                "error": f"Erreur comptage: {str(e)}",
                "data": []
            }), 500

        # Récupération des documents
        try:
            print("🔍 Récupération des documents...")
            cursor = collection.find({}).sort("date_prediction", -1)
            docs = list(cursor)
            print(f"📋 Documents récupérés: {len(docs)}")
            
            if docs:
                print(f"🔍 Premier document brut: {docs[0]}")
                
        except Exception as e:
            print(f"❌ Erreur récupération documents: {e}")
            traceback.print_exc()
            return jsonify({
                "success": False,
                "error": f"Erreur récupération: {str(e)}",
                "data": []
            }), 500

        # Sérialisation
        data = []
        for i, doc in enumerate(docs):
            try:
                serialized = serialize_doc(doc)
                if serialized:
                    data.append(serialized)
                    if i == 0:
                        print(f"✅ Premier document sérialisé: {serialized}")
            except Exception as e:
                print(f"❌ Erreur sérialisation doc {i}: {e}")
                continue

        response = {
            "success": True,
            "data": data,
            "total": len(data),
            "message": f"{len(data)} prédiction(s) récupérée(s)"
        }

        print(f"✅ === RÉPONSE ENVOYÉE: {len(data)} éléments ===")
        return jsonify(response)

    except Exception as e:
        print(f"❌ === ERREUR GÉNÉRALE GET_PREDICTIONS: {e} ===")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Erreur serveur: {str(e)}",
            "data": []
        }), 500

@get_data_bp.route('/predictions/delete', methods=['DELETE'])
def delete_prediction():
    """Supprime une prédiction"""
    try:
        print("🗑️ === DÉBUT DELETE_PREDICTION ===")
        
        collection = get_predictions_collection()
        if collection is None:
            return jsonify({"success": False, "error": "Collection inaccessible"}), 500

        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Données JSON manquantes"}), 400

        print(f"🔍 Données reçues: {data}")

        email = data.get('email_agriculteur')
        azote_n = data.get('azote_n')
        phosphore_p = data.get('phosphore_p')

        if not email or azote_n is None or phosphore_p is None:
            return jsonify({
                "success": False, 
                "error": "Tous les champs requis manquants"
            }), 400

        # Critères de suppression
        query = {
            "email_agriculteur": email,
            "azote_n": float(azote_n),
            "phosphore_p": float(phosphore_p)
        }

        print(f"🔍 Query suppression: {query}")

        # Vérifier existence
        existing_doc = collection.find_one(query)
        if existing_doc:
            print(f"✅ Document trouvé: {existing_doc.get('nom_agriculteur', 'N/A')}")
        else:
            print("⚠️ Document non trouvé")
            return jsonify({"success": False, "error": "Prédiction non trouvée"}), 404

        # Suppression
        result = collection.delete_one(query)
        
        if result.deleted_count > 0:
            print("✅ Suppression réussie")
            return jsonify({
                "success": True,
                "deleted_count": result.deleted_count,
                "message": "Prédiction supprimée"
            })
        else:
            return jsonify({"success": False, "error": "Échec suppression"}), 500

    except Exception as e:
        print(f"❌ Erreur delete: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": f"Erreur: {str(e)}"}), 500

@get_data_bp.route('/predictions/clear', methods=['DELETE'])
def clear_predictions():
    """Supprime toutes les prédictions"""
    try:
        print("🗑️ === DÉBUT CLEAR_PREDICTIONS ===")
        
        collection = get_predictions_collection()
        if collection is None:
            return jsonify({"success": False, "error": "Collection inaccessible"}), 500

        # Comptage avant suppression
        count_before = collection.count_documents({})
        print(f"📊 Documents à supprimer: {count_before}")
        
        if count_before == 0:
            return jsonify({
                "success": True,
                "deleted_count": 0,
                "message": "Aucune prédiction à supprimer"
            })
        
        # Suppression
        result = collection.delete_many({})
        
        print(f"✅ {result.deleted_count} prédictions supprimées")
        return jsonify({
            "success": True,
            "deleted_count": result.deleted_count,
            "message": f"{result.deleted_count} prédiction(s) supprimée(s)"
        })

    except Exception as e:
        print(f"❌ Erreur clear: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": f"Erreur: {str(e)}"}), 500

# Route de test pour insérer des données factices
@get_data_bp.route('/predictions/test-insert', methods=['POST'])
def test_insert():
    """Insère des données de test"""
    try:
        collection = get_predictions_collection()
        if collection is None:
            return jsonify({"success": False, "error": "Collection inaccessible"}), 500

        test_data = {
            'email_agriculteur': 'sophie.durand@example.com',
            'nom_agriculteur': 'Sophie Durand',
            'azote_n': 55,
            'phosphore_p': 45,
            'potassium_k': 40,
            'temperature_celsius': 20.8,
            'humidite_pourcentage': 60,
            'ph_sol': 7,
            'pluie_mensuelle_mm': 80,
            'pluie_annuelle_mm': 800,
            'besoin_irrigation': 'Oui, irrigation importante',
            'culture_recommandee': 'apple',
            'date_prediction': datetime.utcnow(),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        result = collection.insert_one(test_data)
        
        if result.inserted_id:
            return jsonify({
                "success": True,
                "message": "Données test insérées",
                "inserted_id": str(result.inserted_id)
            })
        else:
            return jsonify({"success": False, "error": "Échec insertion"})

    except Exception as e:
        print(f"❌ Erreur test-insert: {e}")
        return jsonify({"success": False, "error": str(e)}), 500 