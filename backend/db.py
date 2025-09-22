# db.py
from pymongo import MongoClient
import pymongo
from datetime import datetime

class Database:
    def __init__(self, uri="mongodb://localhost:27017/", db_name="basejwt"):
        """
        Initialise la connexion à MongoDB avec gestion d'erreurs améliorée
        """
        self.uri = uri
        self.db_name = db_name
        self.client = None
        self.db = None
        
        try:
            # Connexion avec timeout
            self.client = MongoClient(
                uri, 
                serverSelectionTimeoutMS=5000,  # Timeout de 5 secondes
                connectTimeoutMS=10000,         # Timeout de connexion
                socketTimeoutMS=10000           # Timeout de socket
            )
            
            # Sélection de la base de données
            self.db = self.client[db_name]
            
            # Test de connexion
            self.client.admin.command('ping')
            print(f"✅ Connexion réussie à MongoDB")
            print(f"📊 Base de données: '{db_name}'")
            print(f"🔗 URI: {uri}")
            
            # Initialisation des collections et indexes
            self._setup_collections()
            
        except Exception as e:
            print(f"❌ Erreur de connexion MongoDB : {e}")
            self.client = None
            self.db = None
            
    def _setup_collections(self):
        """
        Configuration des collections et création des index
        """
        try:
            if self.db is None:
                return
                
            # Collection des utilisateurs
            users_collection = self.db['users']
            # Index unique sur email
            try:
                users_collection.create_index("email", unique=True)
                print("📋 Collection 'users' configurée avec index unique sur 'email'")
            except Exception as e:
                print(f"⚠️ Index 'users' déjà existant ou erreur: {e}")
            
            # Collection des prédictions
            predictions_collection = self.db['predictions']
            # Index composé pour optimiser les requêtes
            try:
                predictions_collection.create_index([
                    ("id_agriculteur", pymongo.ASCENDING),
                    ("date_prediction", pymongo.DESCENDING)
                ])
                # Index sur email pour les recherches
                predictions_collection.create_index("email_agriculteur")
                print("📋 Collection 'predictions' configurée avec index composé")
            except Exception as e:
                print(f"⚠️ Index 'predictions' déjà existant ou erreur: {e}")
            
            # Affichage des collections existantes
            collections = self.db.list_collection_names()
            print(f"📚 Collections disponibles: {collections}")
            
        except Exception as e:
            print(f"⚠️ Erreur configuration collections: {e}")
    
    def get_collection(self, collection_name):
        """
        Retourne une collection spécifique avec vérification - CORRIGÉ
        """
        if self.db is None:
            print(f"❌ Base de données non connectée")
            return None
            
        try:
            collection = self.db[collection_name]
            print(f"📂 Accès à la collection '{collection_name}'")
            return collection
        except Exception as e:
            print(f"❌ Erreur accès collection '{collection_name}': {e}")
            return None
    
    def test_connection(self):
        """
        Test de connexion et retour du statut
        """
        try:
            if self.client is not None:
                # Test ping
                self.client.admin.command('ping')
                
                # Info serveur
                server_info = self.client.server_info()
                
                return {
                    'connected': True,
                    'server_version': server_info.get('version', 'unknown'),
                    'database': self.db_name,
                    'collections': self.db.list_collection_names() if self.db is not None else []
                }
            else:
                return {'connected': False, 'error': 'Client non initialisé'}
                
        except Exception as e:
            return {'connected': False, 'error': str(e)}
    
    def get_database_stats(self):
        """
        Statistiques de la base de données
        """
        try:
            if self.db is None:
                return {'error': 'Base de données non connectée'}
            
            stats = self.db.command("dbStats")
            
            # Comptage des documents par collection
            collections_info = {}
            for collection_name in self.db.list_collection_names():
                count = self.db[collection_name].count_documents({})
                collections_info[collection_name] = count
            
            return {
                'database_name': self.db_name,
                'collections': collections_info,
                'total_size_bytes': stats.get('dataSize', 0),
                'total_documents': sum(collections_info.values()),
                'indexes': stats.get('indexes', 0),
                'storage_size_bytes': stats.get('storageSize', 0)
            }
            
        except Exception as e:
            return {'error': f'Erreur récupération stats: {str(e)}'}
    
    def create_user_if_not_exists(self, email, password_hash, name="", role="user"):
        """
        Crée un utilisateur s'il n'existe pas déjà
        """
        try:
            users_collection = self.get_collection('users')
            if users_collection is None:
                return {'success': False, 'error': 'Collection users inaccessible'}
            
            # Vérifier si l'utilisateur existe
            existing_user = users_collection.find_one({'email': email})
            if existing_user:
                return {'success': False, 'error': 'Utilisateur déjà existant'}
            
            # Créer nouvel utilisateur
            user_doc = {
                'email': email,
                'password': password_hash,
                'name': name,
                'role': role,
                'created_at': datetime.utcnow(),
                'last_login': None,
                'is_active': True
            }
            
            result = users_collection.insert_one(user_doc)
            
            if result.inserted_id:
                return {
                    'success': True, 
                    'user_id': str(result.inserted_id),
                    'email': email
                }
            else:
                return {'success': False, 'error': 'Erreur création utilisateur'}
                
        except Exception as e:
            return {'success': False, 'error': f'Erreur base de données: {str(e)}'}
    
    def update_last_login(self, user_id):
        """
        Met à jour la dernière connexion d'un utilisateur
        """
        try:
            from bson import ObjectId
            users_collection = self.get_collection('users')
            
            if users_collection is None:
                return False
            
            result = users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'last_login': datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Erreur update last_login: {e}")
            return False
    
    def close_connection(self):
        """
        Ferme la connexion à MongoDB - CORRIGÉ
        """
        if self.client is not None:
            try:
                self.client.close()
                print("🔌 Connexion MongoDB fermée")
            except Exception as e:
                print(f"⚠️ Erreur fermeture connexion: {e}")
        else:
            print("ℹ️ Aucune connexion active à fermer")
    
    def __del__(self):
        """
        Destructeur pour fermer automatiquement la connexion - CORRIGÉ
        """
        try:
            if hasattr(self, 'client') and self.client is not None:
                self.client.close()
        except Exception:
            pass  # Ignorer les erreurs dans le destructeur 