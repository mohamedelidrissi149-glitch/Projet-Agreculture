# test_insert_data.py
from db import Database
from datetime import datetime
import random

def insert_test_predictions():
    """Insère des données de test dans la collection predictions"""
    try:
        print("🚀 Connexion à la base de données...")
        db = Database()
        collection = db.get_collection('predictions')
        
        if collection is None:
            print("❌ Collection predictions inaccessible")
            return False
        
        print("✅ Collection predictions accessible")
        
        # Vérifier le nombre de documents existants
        existing_count = collection.count_documents({})
        print(f"📊 Documents existants dans la collection: {existing_count}")
        
        # Données de test variées
        test_predictions = [
            {
                'email_agriculteur': 'farmer1@example.com',
                'nom_agriculteur': 'Jean Dupont',
                'azote_n': 80,
                'phosphore_p': 40,
                'potassium_k': 60,
                'temperature_celsius': 25.5,
                'humidite_pourcentage': 70,
                'ph_sol': 6.8,
                'pluie_mensuelle_mm': 120,
                'pluie_annuelle_mm': 1200,
                'besoin_irrigation': 'Oui, irrigation nécessaire',
                'culture_recommandee': 'rice',
                'date_prediction': datetime.utcnow(),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
            },
            {
                'email_agriculteur': 'marie.martin@example.com',
                'nom_agriculteur': 'Marie Martin',
                'azote_n': 65,
                'phosphore_p': 50,
                'potassium_k': 45,
                'temperature_celsius': 22.0,
                'humidite_pourcentage': 65,
                'ph_sol': 7.2,
                'pluie_mensuelle_mm': 90,
                'pluie_annuelle_mm': 950,
                'besoin_irrigation': 'Non, irrigation non nécessaire',
                'culture_recommandee': 'wheat',
                'date_prediction': datetime.utcnow(),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
            },
            {
                'email_agriculteur': 'paul.bernard@example.com',
                'nom_agriculteur': 'Paul Bernard',
                'azote_n': 70,
                'phosphore_p': 35,
                'potassium_k': 55,
                'temperature_celsius': 28.3,
                'humidite_pourcentage': 75,
                'ph_sol': 6.5,
                'pluie_mensuelle_mm': 150,
                'pluie_annuelle_mm': 1500,
                'besoin_irrigation': 'Oui, irrigation modérée',
                'culture_recommandee': 'corn',
                'date_prediction': datetime.utcnow(),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
            },
            {
                'email_agriculteur': 'sophie.durand@example.com',
                'nom_agriculteur': 'Sophie Durand',
                'azote_n': 55,
                'phosphore_p': 45,
                'potassium_k': 40,
                'temperature_celsius': 20.8,
                'humidite_pourcentage': 60,
                'ph_sol': 7.0,
                'pluie_mensuelle_mm': 80,
                'pluie_annuelle_mm': 800,
                'besoin_irrigation': 'Oui, irrigation importante',
                'culture_recommandee': 'apple',
                'date_prediction': datetime.utcnow(),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
            },
            {
                'email_agriculteur': 'thomas.petit@example.com',
                'nom_agriculteur': 'Thomas Petit',
                'azote_n': 90,
                'phosphore_p': 60,
                'potassium_k': 70,
                'temperature_celsius': 26.7,
                'humidite_pourcentage': 80,
                'ph_sol': 6.3,
                'pluie_mensuelle_mm': 110,
                'pluie_annuelle_mm': 1100,
                'besoin_irrigation': 'Non, irrigation non nécessaire',
                'culture_recommandee': 'tomato',
                'date_prediction': datetime.utcnow(),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
            },
            {
                'email_agriculteur': 'alice.bernard@example.com',
                'nom_agriculteur': 'Alice Bernard',
                'azote_n': 75,
                'phosphore_p': 42,
                'potassium_k': 58,
                'temperature_celsius': 24.1,
                'humidite_pourcentage': 68,
                'ph_sol': 6.9,
                'pluie_mensuelle_mm': 105,
                'pluie_annuelle_mm': 1050,
                'besoin_irrigation': 'Oui, irrigation légère',
                'culture_recommandee': 'kidneybeans',
                'date_prediction': datetime.utcnow(),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
            },
            {
                'email_agriculteur': 'pierre.moreau@example.com',
                'nom_agriculteur': 'Pierre Moreau',
                'azote_n': 85,
                'phosphore_p': 48,
                'potassium_k': 62,
                'temperature_celsius': 27.2,
                'humidite_pourcentage': 72,
                'ph_sol': 6.4,
                'pluie_mensuelle_mm': 130,
                'pluie_annuelle_mm': 1350,
                'besoin_irrigation': 'Non, irrigation non nécessaire',
                'culture_recommandee': 'rice',
                'date_prediction': datetime.utcnow(),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
            }
        ]
        
        print(f"📥 Insertion de {len(test_predictions)} prédictions de test...")
        
        # Insérer les données une par une avec vérification
        inserted_count = 0
        for i, prediction in enumerate(test_predictions, 1):
            try:
                result = collection.insert_one(prediction)
                if result.inserted_id:
                    inserted_count += 1
                    print(f"✅ Prédiction {i}/{ len(test_predictions)} insérée: {prediction['nom_agriculteur']}")
                else:
                    print(f"❌ Échec insertion prédiction {i}")
            except Exception as e:
                print(f"❌ Erreur insertion prédiction {i}: {e}")
        
        print(f"📊 Résumé de l'insertion:")
        print(f"   - Prédictions à insérer: {len(test_predictions)}")
        print(f"   - Prédictions insérées: {inserted_count}")
        print(f"   - Échecs: {len(test_predictions) - inserted_count}")
        
        # Vérifier le nouveau total
        new_total = collection.count_documents({})
        print(f"📈 Total de prédictions dans la base: {new_total}")
        print(f"📈 Nouveaux documents ajoutés: {new_total - existing_count}")
        
        return inserted_count > 0
        
    except Exception as e:
        print(f"❌ Erreur lors de l'insertion: {e}")
        return False

def verify_data():
    """Vérifie que les données ont été correctement insérées"""
    try:
        print("\n🔍 Vérification des données insérées...")
        
        db = Database()
        collection = db.get_collection('predictions')
        
        if collection is None:
            print("❌ Collection predictions inaccessible")
            return False
        
        # Compter le total
        total = collection.count_documents({})
        print(f"📊 Total de documents: {total}")
        
        # Afficher quelques exemples
        print("\n📋 Exemples de documents:")
        sample_docs = list(collection.find({}).limit(3))
        
        for i, doc in enumerate(sample_docs, 1):
            print(f"\n📄 Document {i}:")
            print(f"   Email: {doc.get('email_agriculteur', 'N/A')}")
            print(f"   Nom: {doc.get('nom_agriculteur', 'N/A')}")
            print(f"   Culture: {doc.get('culture_recommandee', 'N/A')}")
            print(f"   Azote: {doc.get('azote_n', 'N/A')}")
            print(f"   Date: {doc.get('date_prediction', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False

def clean_test_data():
    """Supprime toutes les données de test (optionnel)"""
    try:
        print("\n🧹 Nettoyage des données de test...")
        
        db = Database()
        collection = db.get_collection('predictions')
        
        if collection is None:
            print("❌ Collection predictions inaccessible")
            return False
        
        # Supprimer tous les documents (attention, ceci supprime TOUT)
        result = collection.delete_many({})
        print(f"🗑️ {result.deleted_count} documents supprimés")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Script d'insertion de données de test pour AgriConnect")
    print("=" * 60)
    
    try:
        # Insérer les données de test
        success = insert_test_predictions()
        
        if success:
            print("\n" + "=" * 60)
            print("✅ Données de test insérées avec succès!")
            
            # Vérifier les données
            verify_data()
            
            print("\n💡 Vous pouvez maintenant:")
            print("   1. Tester votre API: http://localhost:5000/api/predictions")
            print("   2. Tester votre frontend React")
            print("   3. Utiliser l'endpoint de nettoyage si nécessaire")
            
        else:
            print("\n" + "=" * 60)
            print("❌ Échec de l'insertion des données de test")
            print("💡 Vérifiez que:")
            print("   1. MongoDB est démarré")
            print("   2. La base de données 'basejwt' existe")
            print("   3. Les permissions sont correctes")
    
    except KeyboardInterrupt:
        print("\n⚠️ Script interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc() 