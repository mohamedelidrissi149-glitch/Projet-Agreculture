import google.generativeai as genai
import os
from flask import Blueprint, request, jsonify
from auth import token_required
 
# Configuration de la clé API
GOOGLE_API_KEY = 'AIzaSyDy45E9YOGHO9jZ6QOEjLScxW83enGRUcI'
genai.configure(api_key=GOOGLE_API_KEY)

# Créer le blueprint pour les routes Gemini
gemini_bp = Blueprint('gemini', __name__)

def generate_agricultural_advice(form_data: dict, irrigation_prediction: str, crop_prediction: str) -> str:
    """
    Génère des conseils agricoles personnalisés avec Gemini LLM.
    
    Args:
        form_data (dict): Données du formulaire agricole
        irrigation_prediction (str): Prédiction d'irrigation (Oui/Non)
        crop_prediction (str): Culture recommandée
    
    Returns:
        str: Conseils agricoles générés par IA
    """
    
    # Construction du prompt contextualisé
    prompt = f"""
Tu es un expert agronome AI. Analyse ces données agricoles et génère des conseils pratiques en français :

📊 DONNÉES TERRAIN :
• Azote (N) : {form_data.get('Nitrogen', 'N/A')} ppm
• Phosphore (P) : {form_data.get('phosphorous', 'N/A')} ppm  
• Potassium (K) : {form_data.get('Potassium', 'N/A')} ppm
• Température : {form_data.get('temperature', 'N/A')}°C
• Humidité : {form_data.get('humidity', 'N/A')}%
• pH du sol : {form_data.get('ph', 'N/A')}
• Pluie mensuelle : {form_data.get('Rainfall_Mensuel', 'N/A')} mm
• Pluie annuelle : {form_data.get('Rainfall_Annuel', 'N/A')} mm

🤖 PRÉDICTIONS MODÈLE ML :
• Besoin irrigation : {irrigation_prediction}
• Culture recommandée : {crop_prediction}

📋 GÉNÈRE UN GUIDE PRATIQUE INCLUANT :

1. 💧 IRRIGATION
   - Fréquence recommandée cette semaine
   - Quantité d'eau par session (L/m²)
   - Meilleur moment de la journée

2. 🌱 FERTILISATION  
   - Dosage NPK recommandé
   - Noms commerciaux d'engrais adaptés
   - Fréquence d'application

3. 🌾 CONSEILS CULTURE "{crop_prediction}"
   - Techniques spécifiques à cette culture
   - Surveillance des maladies
   - Optimisation du rendement

4. ⚠️ ALERTES & RECOMMANDATIONS
   - Points d'attention selon tes conditions
   - Actions prioritaires cette semaine

Réponds de manière concise, pratique et directement applicable. Maximum 400 mots.
"""

    try:
        # Initialiser le modèle Gemini
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Générer la réponse
        response = model.generate_content(prompt)
        
        if response and response.text:
            return response.text.strip()
        else:
            return "Désolé, impossible de générer des conseils pour le moment. Veuillez réessayer."
            
    except Exception as e:
        print(f"❌ Erreur Gemini API: {e}")
        return f"Erreur lors de la génération des conseils: {str(e)}"

@gemini_bp.route('/api/gemini-advice', methods=['POST'])
@token_required
def get_gemini_advice(current_user):
    """
    Endpoint pour obtenir les conseils agricoles de Gemini
    """
    try:
        # Récupérer les données de la requête
        data = request.get_json()
        
        if not data: 
            return jsonify({
                'success': False,
                'error': 'Aucune donnée reçue'
            }), 400
        
        form_data = data.get('formData', {})
        irrigation_prediction = data.get('irrigationPrediction', 'Non spécifiée')
        crop_recommendation = data.get('cropRecommendation', 'Non spécifiée')
        
        # Validation des données essentielles
        required_fields = ['Nitrogen', 'phosphorous', 'Potassium', 'temperature', 'humidity', 'ph']
        missing_fields = [field for field in required_fields if not form_data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Champs manquants: {", ".join(missing_fields)}'
            }), 400
        
        print(f"🧠 Génération conseils pour utilisateur {current_user['email']}")
        print(f"📊 Données: N={form_data.get('Nitrogen')}, P={form_data.get('phosphorous')}, K={form_data.get('Potassium')}")
        print(f"🤖 Prédictions: Irrigation={irrigation_prediction}, Culture={crop_recommendation}")
        
        # Générer les conseils avec Gemini
        advice = generate_agricultural_advice(form_data, irrigation_prediction, crop_recommendation)
        
        if advice and len(advice) > 10:  # Vérifier que la réponse n'est pas vide
            print("✅ Conseils Gemini générés avec succès")
            return jsonify({
                'success': True,
                'advice': advice,
                'user': current_user['email']
            })
        else:
            print("❌ Réponse Gemini vide ou trop courte")
            return jsonify({
                'success': False,
                'error': 'Réponse IA invalide ou vide'
            }), 500
            
    except Exception as e:
        print(f"💥 Erreur endpoint gemini-advice: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur serveur lors de la génération des conseils'
        }), 500

# Fonction de test (optionnelle)
def test_gemini_advice():
    """
    Fonction de test pour vérifier le bon fonctionnement
    """
    sample_data = {
        "Nitrogen": 45,
        "phosphorous": 35,
        "Potassium": 40,
        "temperature": 22,
        "humidity": 65,
        "ph": 6.8,
        "Rainfall_Mensuel": 75,
        "Rainfall_Annuel": 850
    }
        
    advice = generate_agricultural_advice(sample_data, "Oui", "tomate") 
    print("\n" + "="*50)
    print("🧪 TEST CONSEILS GEMINI")
    print("="*50)
    print(advice)
    print("="*50)   
   
if __name__ == "__main__":     
    # Tester la fonction  
    test_gemini_advice()      
       



        