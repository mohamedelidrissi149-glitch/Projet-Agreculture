# create_admin.py
from db import Database
from werkzeug.security import generate_password_hash, check_password_hash

# Connexion à la base
db = Database()
users_collection = db.get_collection('users')
 
# Vérifier si l'admin existe déjà
existing_admin = users_collection.find_one({"email": "admin@gmail.com"})

if existing_admin:
    print("⚠️ L'administrateur existe déjà. Mise à jour du mot de passe...")
    # Mettre à jour avec un nouveau hash pbkdf2
    new_password_hash = generate_password_hash("admin123", method='pbkdf2:sha256')
    users_collection.update_one(
        {"email": "admin@gmail.com"},
        {"$set": {"password": new_password_hash}}
    )
    print("✅ Mot de passe admin mis à jour avec pbkdf2!")  
else:
    admin_user = {
        "nom": "Admin",  
        "prenom": "Admin", 
        "email": "admin@gmail.com",
        "ville": "Rabat",
        "pays": "Maroc",
        "codePostal": "00000", 
        "password": generate_password_hash("admin123", method='pbkdf2:sha256'),
        "role": "admin"
    }    

    result = users_collection.insert_one(admin_user)
    print(f"✅ Compte admin créé avec succès ! ID: {result.inserted_id}")

# Test de vérification du mot de passe
print("\\n🧪 Test de vérification...")
admin_check = users_collection.find_one({"email": "admin@gmail.com"})
if admin_check:
    stored_hash = admin_check['password']
    test_password = "admin123"
    
    print(f"Hash stocké: {stored_hash[:50]}...")
    is_valid = check_password_hash(stored_hash, test_password)
    print(f"Vérification mot de passe '{test_password}': {'✅ VALIDE' if is_valid else '❌ INVALIDE'}")
    
    print(f"\\n📋 Informations de connexion:")
    print(f"Email: admin@gmail.com")
    print(f"Mot de passe: admin123")
    print(f"Rôle: {admin_check['role']}")
 
db.close_connection() 