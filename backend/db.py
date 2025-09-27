# db.py
from pymongo import MongoClient
import pymongo
from datetime import datetime

# Connexion globale pour réutiliser la même connexion
_global_client = None
_global_db = None

class Database:
    def __init__(self, uri="mongodb://localhost:27017/", db_name="basejwt"):
        """
        Initialise la connexion à MongoDB avec pattern singleton
        """
        global _global_client, _global_db
        self.uri = uri
        self.db_name = db_name

        # Réutiliser la connexion existante si disponible
        if _global_client is not None:
            try:
                _global_client.admin.command('ping')
                self.client = _global_client
                self.db = _global_db
                print("✅ Réutilisation connexion MongoDB existante")
                return
            except Exception as e:
                print(f"⚠️ Connexion globale invalide, recréation: {e}")
                _global_client = None
                _global_db = None

        # Nouvelle connexion MongoDB
        try:
            self.client = MongoClient(
                uri,
                serverSelectionTimeoutMS=5000,  # 5 secondes
                connectTimeoutMS=10000,         # 10 secondes
                socketTimeoutMS=10000,          # 10 secondes
                maxPoolSize=20,                 # Pool de connexions
                minPoolSize=5,
                retryWrites=True
            )
            
            self.db = self.client[db_name]
            
            # Test de connexion
            self.client.admin.command('ping')
            print(f"✅ Nouvelle connexion MongoDB établie: '{db_name}'")

            # Sauvegarder globalement
            _global_client = self.client
            _global_db = self.db

            # Configuration des collections
            self._setup_collections()
            
        except Exception as e:
            print(f"❌ Erreur connexion MongoDB: {e}")
            self.client = None
            self.db = None

    def _setup_collections(self):
        """Configuration automatique des collections et index"""
        if self.db is None:
            return
            
        try:
            # Collection users
            users = self.db['users']
            try:
                users.create_index("email", unique=True)
                print("📋 Index unique sur 'email' configuré")
            except Exception:
                pass  # Index existe déjà

            # Collection predictions
            predictions = self.db['predictions']
            try:
                predictions.create_index([
                    ("email_agriculteur", pymongo.ASCENDING),
                    ("date_prediction", pymongo.DESCENDING)
                ])
                print("📋 Index composé predictions configuré")
            except Exception:
                pass  # Index existe déjà

            collections = self.db.list_collection_names()
            print(f"📚 Collections: {collections}")
            
        except Exception as e:
            print(f"⚠️ Erreur setup collections: {e}")

    def get_collection(self, name):
        """Récupère une collection MongoDB"""
        if self.db is None:
            print("❌ Base de données non connectée")
            return None
            
        try:
            collection = self.db[name]
            print(f"📂 Accès collection '{name}'")
            return collection
        except Exception as e:
            print(f"❌ Erreur accès collection '{name}': {e}")
            return None

    def test_connection(self):
        """Test de santé de la connexion"""
        if self.client is None:
            return {'connected': False, 'error': 'Client non initialisé'}
            
        try:
            self.client.admin.command('ping')
            server_info = self.client.server_info()
            
            return {
                'connected': True,
                'server_version': server_info.get('version', 'unknown'),
                'database': self.db_name,
                'collections': self.db.list_collection_names() if self.db else []
            }
        except Exception as e:
            return {'connected': False, 'error': str(e)}

    def create_user(self, user_data):
        """Créer un nouvel utilisateur"""
        users = self.get_collection('users')
        if users is None:
            return {'success': False, 'error': 'Collection users inaccessible'}
            
        try:
            # Vérifier si l'email existe
            if users.find_one({'email': user_data.get('email')}):
                return {'success': False, 'error': 'Email déjà utilisé'}
            
            # Ajouter timestamp
            user_data['created_at'] = datetime.utcnow()
            user_data['updated_at'] = datetime.utcnow()
            
            result = users.insert_one(user_data)
            
            return {
                'success': True, 
                'user_id': str(result.inserted_id),
                'email': user_data.get('email')
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_all_users(self, projection=None):
        """Récupérer tous les utilisateurs"""
        users = self.get_collection('users')
        if users is None:
            return {'success': False, 'error': 'Collection users inaccessible'}
            
        try:
            if projection is None:
                projection = {
                    "_id": 1, "nom": 1, "prenom": 1, "email": 1,
                    "ville": 1, "pays": 1, "codePostal": 1, "created_at": 1
                }
            
            users_list = list(users.find({}, projection))
            
            # Transformer ObjectId en string
            for user in users_list:
                user["id"] = str(user["_id"])
                del user["_id"]
            
            return {'success': True, 'users': users_list, 'total': len(users_list)}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_user_by_id(self, user_id):
        """Récupérer un utilisateur par son ID"""
        from bson import ObjectId
        users = self.get_collection('users')
        if users is None:
            return {'success': False, 'error': 'Collection users inaccessible'}
            
        try:
            user = users.find_one({"_id": ObjectId(user_id)})
            if not user:
                return {'success': False, 'error': 'Utilisateur introuvable'}
            
            user["id"] = str(user["_id"])
            del user["_id"]
            
            # Ne pas retourner le mot de passe
            if "motDePasse" in user:
                del user["motDePasse"]
            if "password" in user:
                del user["password"]
            
            return {'success': True, 'user': user}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_user(self, user_id, update_data):
        """Mettre à jour un utilisateur"""
        from bson import ObjectId
        users = self.get_collection('users')
        if users is None:
            return {'success': False, 'error': 'Collection users inaccessible'}
            
        try:
            # Ajouter timestamp de mise à jour
            update_data['updated_at'] = datetime.utcnow()
            
            result = users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {'success': False, 'error': 'Utilisateur introuvable'}
            
            return {'success': True, 'modified': result.modified_count > 0}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def delete_user(self, user_id):
        """Supprimer un utilisateur"""
        from bson import ObjectId
        users = self.get_collection('users')
        if users is None:
            return {'success': False, 'error': 'Collection users inaccessible'}
            
        try:
            result = users.delete_one({"_id": ObjectId(user_id)})
            
            if result.deleted_count == 0:
                return {'success': False, 'error': 'Utilisateur introuvable'}
            
            return {'success': True, 'deleted': True}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_user_stats(self):
        """Statistiques des utilisateurs"""
        users = self.get_collection('users')
        if users is None:
            return {'success': False, 'error': 'Collection users inaccessible'}
            
        try:
            total = users.count_documents({})
            
            # Grouper par pays
            pipeline = [
                {"$group": {"_id": "$pays", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            
            by_country = list(users.aggregate(pipeline))
            
            return {
                'success': True,
                'total_users': total,
                'by_country': by_country
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def close_connection(self):
        """Fermeture de connexion - maintient le singleton"""  
        print("🔌 Connexion maintenue (pattern singleton)")    
        # Ne ferme pas la connexion globale pour la réutiliser  

    def __del__(self):
        """Destructeur - ne ferme pas la connexion globale""" 
        pass         