# db.py
from pymongo import MongoClient
import pymongo

class Database:
    def __init__(self, uri="mongodb://localhost:27017/", db_name="basejwt"):
        """
        Initialise la connexion à MongoDB 
        """
        try:
            self.client = MongoClient(uri)
            self.db = self.client[db_name]
            # Test de connexion
            self.client.admin.command('ping')
            print(f"✅ Connexion réussie à la base '{db_name}'")
        except Exception as e:
            print(f"❌ Erreur de connexion MongoDB : {e}")

    def get_collection(self, collection_name): 
        """
        Retourne une collection spécifique
        """
        return self.db[collection_name]
    
    def close_connection(self):
        """
        Ferme la connexion à MongoDB
        """
        if self.client:
            self.client.close()  