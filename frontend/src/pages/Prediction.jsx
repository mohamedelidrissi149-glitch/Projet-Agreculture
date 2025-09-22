import React, { useState, useEffect } from "react";
import "./Prediction.css"; // import du CSS
import Navbar from "../components/Navbar"; // Import du Navbar
import Footer from "../components/Footer"; // Import du Footer
import SidebarClient from "../components/SidebarClient"; // Import du nouveau Sidebar
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {  
  faFlask, faVial, faAtom, faThermometerHalf, faTint, faBalanceScale, 
  faCloudRain, faUmbrella, faSeedling, faMagic, faChartLine, faBrain, 
  faLeaf, faSave, faClock, faExclamationTriangle, faAppleAlt, faCarrot, 
  faPepperHot, faBreadSlice, faRobot, faLightbulb, faComments, faUser,
  faTrash, faDroplet, faCalculator, faCalendarAlt, faDatabase, faCheckCircle
} from '@fortawesome/free-solid-svg-icons';
import { useNavigate } from 'react-router-dom';
import axios from "axios";

const Prediction = () => { 
  const [formData, setFormData] = useState({
    Nitrogen: "",
    phosphorous: "",
    Potassium: "",
    temperature: "", 
    humidity: "",
    ph: "",
    Rainfall_Mensuel: "",
    Rainfall_Annuel: "",  
  });

  const [prediction, setPrediction] = useState(null);
  const [cropRecommendation, setCropRecommendation] = useState(null);
  const [geminiAdvice, setGeminiAdvice] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [cropErrorMsg, setCropErrorMsg] = useState(null);
  const [geminiErrorMsg, setGeminiErrorMsg] = useState(null);
  const [userData, setUserData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isGeminiLoading, setIsGeminiLoading] = useState(false);
  
  // État pour gérer le sidebar
  const [activeSection, setActiveSection] = useState('prediction');
  
  // États pour la sauvegarde automatique
  const [savedToDB, setSavedToDB] = useState(false);
  const [predictionId, setPredictionId] = useState(null);
  
  const navigate = useNavigate();

  // Historique chargé depuis la base de données
  const [historique, setHistorique] = useState([]);
  const [historiqueLoading, setHistoriqueLoading] = useState(false);
  
  // Statistiques utilisateur
  const [userStats, setUserStats] = useState({
    totalAnalyses: 0,
    irrigationOui: 0,
    irrigationNon: 0,
    pourcentageIrrigation: 0
  });

  // Vérification de l'authentification au chargement
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    const user = localStorage.getItem('userData');
    
    if (!token || !user) {
      console.log('Pas de token ou données utilisateur');
      navigate('/login');
      return;
    }
    
    try {
      const parsedUser = JSON.parse(user);
      setUserData(parsedUser);
      console.log('Utilisateur connecté:', parsedUser.email);
      
      // Charger l'historique et stats au démarrage
      loadUserHistory();
      loadUserStats();
      
    } catch (error) {
      console.log('Erreur parsing user data');
      localStorage.removeItem('authToken');
      localStorage.removeItem('userData');
      navigate('/login');
    }
  }, [navigate]);

  // Fonction pour charger l'historique depuis la base de données
  const loadUserHistory = async () => {
    setHistoriqueLoading(true);
    try {
      const token = localStorage.getItem('authToken');
      
      const response = await fetch("http://localhost:5000/api/get-my-predictions", {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        }
      });
      
      const data = await response.json();
      
      if (data.success && data.predictions) {
        // Transformation pour correspondre à l'ancien format
        const transformedHistory = data.predictions.map(pred => ({
          id: pred._id,
          date: pred.date_prediction.split('T')[0],
          azote: pred.azote_n,
          phosphore: pred.phosphore_p,
          potassium: pred.potassium_k,
          temperature: pred.temperature_celsius,
          humidite: pred.humidite_pourcentage,
          ph: pred.ph_sol,
          pluieMensuelle: pred.pluie_mensuelle_mm,
          pluieAnnuelle: pred.pluie_annuelle_mm,
          besoinIrrigation: pred.besoin_irrigation.includes("Oui") ? "Oui" : "Non",
          cultureRecommandee: pred.culture_recommandee
        }));
        
        setHistorique(transformedHistory);
        console.log(`Historique chargé: ${transformedHistory.length} prédictions`);
      } else {
        console.log('Aucun historique trouvé');
        setHistorique([]);
      }
      
    } catch (error) {
      console.error('Erreur chargement historique:', error);
      setHistorique([]);
    } finally {
      setHistoriqueLoading(false);
    }
  };

  // Fonction pour charger les statistiques utilisateur
  const loadUserStats = async () => {
    try {
      const token = localStorage.getItem('authToken');
      const user = JSON.parse(localStorage.getItem('userData'));
      
      const response = await fetch(`http://localhost:5000/api/stats/${user.id}`, {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        }
      });
      
      const data = await response.json();
      
      if (data.success && data.stats) {
        setUserStats({
          totalAnalyses: data.stats.total_predictions,
          irrigationOui: data.stats.irrigation_oui,
          irrigationNon: data.stats.irrigation_non,
          pourcentageIrrigation: data.stats.pourcentage_irrigation
        });
        console.log('Statistiques chargées:', data.stats);
      }
      
    } catch (error) {
      console.error('Erreur chargement statistiques:', error);
    }
  };

  // Gestionnaire pour changer de section
  const handleSectionChange = (section) => {
    setActiveSection(section);
    console.log('Section changée vers:', section);
    
    // Recharger les données si nécessaire
    if (section === 'historique') {
      loadUserHistory();
      loadUserStats();
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // Fonction pour supprimer une entrée de l'historique
  const handleDelete = async (id) => {
    try {
      const token = localStorage.getItem('authToken');
      
      const response = await fetch(`http://localhost:5000/api/delete-prediction/${id}`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        }
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Supprimer de l'état local
        setHistorique(prev => prev.filter(item => item.id !== id));
        console.log('Entrée supprimée:', id);
        
        // Recharger les statistiques
        loadUserStats();
      } else {
        console.error('Erreur suppression:', data.error);
      }
      
    } catch (error) {
      console.error('Erreur suppression:', error);
    }
  };

  // Fonction pour obtenir les détails de la culture
  const getCropDetails = (cropName) => {
    const cropData = {
      'pomme': { 
        icon: faAppleAlt, 
        emoji: '🍎', 
        color: '#ff6b6b',
        description: 'Culture fruitière adaptée aux climats tempérés'
      },
      'apple': { 
        icon: faAppleAlt, 
        emoji: '🍎', 
        color: '#ff6b6b',
        description: 'Culture fruitière adaptée aux climats tempérés'
      },
      'fraise': { 
        icon: faLeaf, 
        emoji: '🍓', 
        color: '#ff1744',
        description: 'Fruit rouge riche en vitamines'
      },
      'tomate': { 
        icon: faPepperHot, 
        emoji: '🍅', 
        color: '#f44336',
        description: 'Légume-fruit polyvalent'
      },
      'carotte': { 
        icon: faCarrot, 
        emoji: '🥕', 
        color: '#ff9800',
        description: 'Légume racine riche en carotène'
      },
      'blé': { 
        icon: faBreadSlice, 
        emoji: '🌾', 
        color: '#ffc107',
        description: 'Céréale de base pour l\'alimentation'
      },
      'maïs': { 
        icon: faSeedling, 
        emoji: '🌽', 
        color: '#ffeb3b',
        description: 'Céréale énergétique'
      },
      'maize': { 
        icon: faSeedling, 
        emoji: '🌽', 
        color: '#ffeb3b',
        description: 'Céréale énergétique'
      },
      'rice': { 
        icon: faBreadSlice, 
        emoji: '🍚', 
        color: '#ffc107',
        description: 'Céréale de base asiatique'
      },
      'banana': { 
        icon: faLeaf, 
        emoji: '🍌', 
        color: '#ffeb3b',
        description: 'Fruit tropical nutritif'
      },
      'salade': { 
        icon: faLeaf, 
        emoji: '🥬', 
        color: '#4caf50',
        description: 'Légume feuille à croissance rapide'
      },
      'courgette': { 
        icon: faLeaf, 
        emoji: '🥒', 
        color: '#8bc34a',
        description: 'Légume vert polyvalent'
      }
    };
    
    const lowerCropName = cropName.toLowerCase();
    return cropData[lowerCropName] || { 
      icon: faSeedling, 
      emoji: '🌱', 
      color: '#4caf50',
      description: 'Culture recommandée selon vos paramètres'
    };
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    // Reset des états d'erreur
    setErrorMsg(null);
    setCropErrorMsg(null);
    setGeminiErrorMsg(null);
    setSavedToDB(false);
    setPredictionId(null);
    
    try {
      const token = localStorage.getItem('authToken');
      
      if (!token) {
        setErrorMsg("Session expirée, veuillez vous reconnecter");
        navigate('/login');
        return;
      }
       
      console.log('Envoi de la prédiction complète...');
      
      // 🚀 NOUVELLE APPROCHE: Utiliser l'endpoint combiné
      try {
        const response = await fetch("http://localhost:5000/api/complete-prediction", {
          method: "POST",
          headers: { 
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
          },
          body: JSON.stringify(formData),
        });
        
        const data = await response.json();
        
        if (response.status === 401) {
          setErrorMsg("Session expirée, veuillez vous reconnecter");
          localStorage.removeItem('authToken');
          localStorage.removeItem('userData');
          navigate('/login');
          return;
        }
        
        if (data.success) {
          // Traitement des résultats
          setPrediction(data.irrigation_prediction);
          setCropRecommendation(data.crop_recommendation);
          setSavedToDB(data.saved_to_db);
          setPredictionId(data.prediction_id);
          
          console.log('Prédiction complète reçue:', {
            irrigation: data.irrigation_prediction,
            crop: data.crop_recommendation,
            saved: data.saved_to_db,
            id: data.prediction_id
          });
          
          // Recharger l'historique si sauvegardé
          if (data.saved_to_db) {
            setTimeout(() => {
              loadUserHistory();
              loadUserStats();
            }, 500);
          }
          
        } else {
          setErrorMsg(data.error || "Erreur lors de la prédiction");
          console.log('Erreur prédiction complète:', data.error);
        }
        
      } catch (error) {
        setErrorMsg("Erreur de connexion au serveur");
        console.error('Erreur prédiction complète:', error);
      }

      // Appel pour les conseils Gemini LLM (séparément)
      if (prediction || cropRecommendation) {
        setIsGeminiLoading(true);
        try {
          const geminiResponse = await fetch("http://localhost:5000/api/gemini-advice", {
            method: "POST",
            headers: { 
              "Content-Type": "application/json",
              "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
              formData: formData,
              irrigationPrediction: prediction,
              cropRecommendation: cropRecommendation
            }),
          });
          
          const geminiData = await geminiResponse.json();
          
          if (geminiData.success && geminiData.advice) {
            setGeminiAdvice(geminiData.advice);
            console.log('Conseils Gemini reçus');
          } else {
            setGeminiAdvice(null);
            setGeminiErrorMsg(geminiData.error || "Erreur lors de la génération des conseils");
            console.log('Erreur conseils Gemini:', geminiData.error);
          }
          
        } catch (error) {
          setGeminiAdvice(null);
          setGeminiErrorMsg("Service de conseils IA temporairement indisponible");
          console.error('Erreur conseils Gemini:', error);
        } finally {
          setIsGeminiLoading(false);
        }
      }
      
    } catch (error) {
      setPrediction(null);
      setCropRecommendation(null);
      setErrorMsg("Erreur réseau ou serveur indisponible");
      console.error('Erreur réseau générale:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fields = [
    { label: "Azote (N)", name: "Nitrogen", icon: faFlask },
    { label: "Phosphore (P)", name: "phosphorous", icon: faVial },
    { label: "Potassium (K)", name: "Potassium", icon: faAtom },
    { label: "Température (°C)", name: "temperature", icon: faThermometerHalf },
    { label: "Humidité (%)", name: "humidity", icon: faTint },
    { label: "pH du sol", name: "ph", icon: faBalanceScale },
    { label: "Pluie mensuelle (mm)", name: "Rainfall_Mensuel", icon: faCloudRain },
    { label: "Pluie annuelle (mm)", name: "Rainfall_Annuel", icon: faUmbrella },
  ]; 

  const infoCards = [
    { title: "IA Avancée", text: "Algorithme d'apprentissage automatique", icon: faBrain },
    { title: "Précision", text: "Analyse multi-paramètres précise", icon: faLeaf },
    { title: "Sauvegarde", text: "Historique automatiquement sauvegardé", icon: faDatabase },
    { title: "Temps Réel", text: "Prédictions instantanées", icon: faClock },
  ];

  // Fonction pour rendre le contenu selon la section active 
  const renderContent = () => {
    switch(activeSection) {
      case 'historique':
        return (
          <div className="prediction-content-section">
            <div className="prediction-section-header">
              <h2>📊 Historique des Prédictions</h2>
              <p>Consultez vos analyses sauvegardées dans la base de données MongoDB</p>
            </div>

            {/* Cartes de statistiques */}
            <div className="prediction-stats-grid">
              <div className="prediction-stats-card prediction-stats-total">
                <div className="prediction-stats-icon">
                  <FontAwesomeIcon icon={faCalculator} />
                </div>
                <div className="prediction-stats-content">
                  <h3>{userStats.totalAnalyses}</h3>
                  <p>Total des Analyses</p>
                  <small>Sauvegardées en base</small>
                </div>
              </div>

              <div className="prediction-stats-card prediction-stats-irrigation">
                <div className="prediction-stats-icon">
                  <FontAwesomeIcon icon={faDroplet} />
                </div>
                <div className="prediction-stats-content">
                  <h3>{userStats.irrigationOui}</h3>
                  <p>Besoin d'Irrigation</p>
                  <small>{userStats.pourcentageIrrigation}% des analyses</small>
                </div>
              </div>

              <div className="prediction-stats-card prediction-stats-no-irrigation">
                <div className="prediction-stats-icon">
                  <FontAwesomeIcon icon={faSeedling} />
                </div>
                <div className="prediction-stats-content">
                  <h3>{userStats.irrigationNon}</h3>
                  <p>Pas d'Irrigation</p>
                  <small>{100 - userStats.pourcentageIrrigation}% des analyses</small>
                </div>
              </div>

              <div className="prediction-stats-card prediction-stats-date">
                <div className="prediction-stats-icon">
                  <FontAwesomeIcon icon={faDatabase} />
                </div>
                <div className="prediction-stats-content">
                  <h3>MongoDB</h3>
                  <p>Base de Données</p>
                  <small>Synchronisé automatiquement</small>
                </div>
              </div>
            </div>

            {/* Tableau historique */}
            <div className="prediction-history-table-container">
              <div className="prediction-table-header">
                <h3>📋 Historique Complet MongoDB</h3>
                <p>Toutes vos prédictions sauvegardées automatiquement</p>
                {historiqueLoading && <span>🔄 Chargement...</span>}
              </div>

              {historique && historique.length > 0 ? (
                <div className="prediction-table-wrapper">
                  <table className="prediction-history-table">
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>Azote (N)</th>
                        <th>Phosphore (P)</th>
                        <th>Potassium (K)</th>
                        <th>Temp. °C</th>
                        <th>Humidité %</th>
                        <th>pH</th>
                        <th>Pluie M. (mm)</th>
                        <th>Pluie A. (mm)</th>
                        <th>Irrigation</th>
                        <th>Culture</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {historique.map((item) => (
                        <tr key={item.id}>
                          <td>
                            <span className="prediction-date-badge">
                              <FontAwesomeIcon icon={faCalendarAlt} />
                              {item.date}
                            </span>
                          </td>
                          <td><span className="prediction-value">{item.azote}</span></td>
                          <td><span className="prediction-value">{item.phosphore}</span></td>
                          <td><span className="prediction-value">{item.potassium}</span></td>
                          <td><span className="prediction-value">{item.temperature}</span></td>
                          <td><span className="prediction-value">{item.humidite}</span></td>
                          <td><span className="prediction-value">{item.ph}</span></td>
                          <td><span className="prediction-value">{item.pluieMensuelle}</span></td>
                          <td><span className="prediction-value">{item.pluieAnnuelle}</span></td>
                          <td>
                            <span className={`prediction-irrigation-badge ${item.besoinIrrigation === "Oui" ? "prediction-irrigation-yes" : "prediction-irrigation-no"}`}>
                              <FontAwesomeIcon icon={item.besoinIrrigation === "Oui" ? faDroplet : faSeedling} />
                              {item.besoinIrrigation}
                            </span>
                          </td>
                          <td>
                            <span className="prediction-crop-badge">
                              {getCropDetails(item.cultureRecommandee).emoji}
                              {item.cultureRecommandee}
                            </span>
                          </td>
                          <td>
                            <button
                              onClick={() => handleDelete(item.id)}
                              className="prediction-delete-btn"
                              title="Supprimer de MongoDB"
                            >
                              <FontAwesomeIcon icon={faTrash} />
                              Supprimer
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="prediction-placeholder-card">
                  <FontAwesomeIcon icon={faDatabase} className="prediction-placeholder-icon"/>
                  <h3>Aucune prédiction sauvegardée</h3>
                  <p>Effectuez votre première analyse pour voir les données MongoDB ici.</p>
                  <p>Les prédictions sont automatiquement sauvegardées lors des analyses.</p>
                </div>
              )}
            </div>
          </div> 
        );     

      case 'profile':
        return (
          <div className="prediction-content-section">
            <div className="prediction-section-header">
              <h2>👤 Profil Utilisateur</h2>
              <p>Gérez vos informations personnelles et paramètres</p>
            </div>
            <div className="prediction-profile-placeholder">
              <div className="prediction-placeholder-card">
                <FontAwesomeIcon icon={faUser} className="prediction-placeholder-icon"/>
                <h3>Profil utilisateur</h3>
                {userData && (
                  <div className="prediction-user-info">
                    <p><strong>Email:</strong> {userData.email}</p>
                    <p><strong>Nom:</strong> {userData.name || 'Non renseigné'}</p>
                    <p><strong>Analyses effectuées:</strong> {userStats.totalAnalyses}</p>
                    <p><strong>Dernière connexion:</strong> {new Date().toLocaleDateString()}</p>
                    <p><strong>Données sauvegardées:</strong> MongoDB</p>
                  </div>
                )}
                <p>Paramètres et informations du profil à venir.</p>
              </div>
            </div>
          </div>
        );
      
      default: // Section prédiction par défaut
        return (
          <div className="prediction-three-column-layout">
            {/* Section Formulaire à gauche */}
            <div className="prediction-form-section">
              <div className="prediction-form">
                <h2 className="prediction-form-title">
                  <FontAwesomeIcon icon={faSeedling}/> Analyse Agricole Intelligente
                </h2>
                <p className="prediction-form-subtitle">
                  Entrez les paramètres pour obtenir des recommandations avec sauvegarde automatique MongoDB
                </p>
                
                {/* Indicateur de sauvegarde */}
                {savedToDB && predictionId && (
                  <div className="prediction-save-success">
                    <FontAwesomeIcon icon={faCheckCircle} />
                    <span>Prédiction sauvegardée automatiquement (ID: {predictionId.substring(0, 8)}...)</span>
                  </div>
                )}
                
                <form onSubmit={handleSubmit} className="prediction-form-grid">
                  {fields.map(field => (
                    <div key={field.name} className="prediction-form-group">
                      <label htmlFor={field.name}>{field.label}</label>
                      <div className="prediction-input-wrapper">
                        <FontAwesomeIcon icon={field.icon} className="prediction-input-icon"/>
                        <input
                          type="number"
                          step="any"
                          id={field.name}
                          name={field.name}
                          placeholder={field.label}
                          value={formData[field.name]}
                          onChange={handleChange}
                          required
                        />
                      </div>
                    </div>
                  ))}
                  <button type="submit" className="prediction-submit-btn" disabled={isLoading}>
                    <FontAwesomeIcon icon={faMagic}/> 
                    {isLoading ? 'Analyse & Sauvegarde...' : 'Analyser avec Sauvegarde'}
                  </button>
                </form>

                {/* Info cards sous le formulaire */}
                <div className="prediction-info-cards">
                  {infoCards.map(card => (
                    <div key={card.title} className="prediction-info-card">
                      <FontAwesomeIcon icon={card.icon} className="prediction-info-card-icon"/>
                      <div className="prediction-info-card-title">{card.title}</div>
                      <div className="prediction-info-card-text">{card.text}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Section Résultats au milieu */}
            <div className="prediction-results-section">
              <h2 className="prediction-results-title">
                <FontAwesomeIcon icon={faChartLine}/> Résultats ML + MongoDB
              </h2>

              {isLoading ? (
                <div className="prediction-loading-container">
                  <div className="prediction-result-card">
                    <div className="prediction-result-icon">⏳</div>
                    <div className="prediction-result-text">Analyse en cours...</div>
                    <div className="prediction-result-description">
                      Prédiction ML + sauvegarde automatique MongoDB
                    </div>
                  </div>
                </div>
              ) : (
                <>
                  {/* Layout vertical pour les résultats */}
                  <div className="prediction-results-vertical">
                    {/* Section Irrigation */}
                    <div className="prediction-irrigation-section">
                      <h3 className="prediction-section-title">
                        💧 Besoin d'Irrigation
                      </h3>
                      {errorMsg ? (
                        <div className="prediction-error-card">
                          <FontAwesomeIcon icon={faExclamationTriangle} className="prediction-result-icon"/>
                          <div><strong>Erreur :</strong> {errorMsg}</div>
                        </div>
                      ) : prediction ? (
                        <div className={`prediction-result-card ${prediction.includes("Oui") ? "success" : "info"}`}>
                          <div className="prediction-result-icon">
                            {prediction.includes("Oui") ? "💧" : "🌱"}
                          </div>
                          <div className="prediction-result-text">{prediction}</div>
                          <div className="prediction-result-description">
                            {prediction.includes("Oui") ? 
                              "Votre culture nécessite un arrosage." : 
                              "Pas besoin d'irrigation supplémentaire."}
                          </div>
                          {savedToDB && (
                            <div className="prediction-save-indicator">
                              <FontAwesomeIcon icon={faDatabase} />
                              <span>Sauvegardé en MongoDB</span>
                            </div>
                          )}
                        </div>
                      ) : (
                        <div className="prediction-result-card">
                          <div className="prediction-result-icon">🤖</div>
                          <div className="prediction-result-text">En attente d'analyse</div>
                          <div className="prediction-result-description">
                            Remplissez le formulaire pour une analyse avec sauvegarde automatique.
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Section Culture */}
                    <div className="prediction-crop-section">
                      <h3 className="prediction-section-title">
                        🌾 Culture Recommandée
                      </h3>
                      {cropErrorMsg ? (
                        <div className="prediction-warning-card">
                          <FontAwesomeIcon icon={faExclamationTriangle} className="prediction-result-icon"/>
                          <div className="prediction-result-text">Service temporairement indisponible</div>
                          <div className="prediction-result-description">
                            {cropErrorMsg}
                          </div>
                        </div>
                      ) : cropRecommendation ? (
                        <div className="prediction-crop-card">
                          <div className="prediction-crop-icon">
                            {getCropDetails(cropRecommendation).emoji}
                          </div>
                          <div className="prediction-crop-name">
                            {cropRecommendation.charAt(0).toUpperCase() + cropRecommendation.slice(1)}
                          </div>
                          <div className="prediction-crop-description">
                            {getCropDetails(cropRecommendation).description}
                          </div>
                          <div className="prediction-crop-badge">
                            ✅ Culture optimale pour vos conditions
                          </div>
                          {savedToDB && (
                            <div className="prediction-save-indicator">
                              <FontAwesomeIcon icon={faDatabase} />
                              <span>Sauvegardé en MongoDB</span>
                            </div>
                          )}
                        </div>
                      ) : (
                        <div className="prediction-result-card">
                          <div className="prediction-result-icon">🌾</div>
                          <div className="prediction-result-text">En attente d'analyse</div>
                          <div className="prediction-result-description">
                            Analyse des conditions pour recommander une culture.
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </>
              )}
            </div>

            {/* Section Conseils IA à droite */}
            <div className="prediction-gemini-section">
              <h2 className="prediction-gemini-title">
                <FontAwesomeIcon icon={faRobot}/> Conseils IA Expert
              </h2>

              {isGeminiLoading ? (
                <div className="prediction-gemini-loading">
                  <div className="prediction-gemini-card">
                    <div className="prediction-gemini-icon">🧠</div>
                    <div className="prediction-gemini-text">IA en réflexion...</div>
                    <div className="prediction-gemini-description">
                      Génération de conseils personnalisés en cours...
                    </div>
                    <div className="prediction-gemini-spinner"></div>
                  </div>
                </div>
              ) : geminiErrorMsg ? (
                <div className="prediction-gemini-error">
                  <FontAwesomeIcon icon={faExclamationTriangle} className="prediction-gemini-error-icon"/>
                  <div className="prediction-gemini-error-text">Service IA indisponible</div>
                  <div className="prediction-gemini-error-description">{geminiErrorMsg}</div>
                </div>
              ) : geminiAdvice ? (
                <div className="prediction-gemini-advice">
                  <div className="prediction-gemini-header">
                    <FontAwesomeIcon icon={faLightbulb} className="prediction-gemini-advice-icon"/>
                    <span>Conseils Personnalisés</span>
                  </div>
                  <div className="prediction-gemini-content">
                    {geminiAdvice.split('\n').map((line, index) => (
                      <p key={index} className="prediction-gemini-line">
                        {line}
                      </p>
                    ))}
                  </div> 
                  <div className="prediction-gemini-footer">
                    <FontAwesomeIcon icon={faComments} className="prediction-gemini-footer-icon"/>
                    <span>Généré par IA Gemini</span>
                  </div>
                </div>
              ) : (
                <div className="prediction-gemini-waiting">
                  <div className="prediction-gemini-card">
                    <div className="prediction-gemini-icon">🤖</div>
                    <div className="prediction-gemini-text">Conseils IA en attente</div>
                    <div className="prediction-gemini-description">
                      Soumettez le formulaire pour obtenir des conseils personnalisés d'un expert IA en agriculture.
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        );
    }
  };  

  return (
    <div className="prediction-page">
      {/* Navigation Bar */}
      <Navbar /> 
      
      {/* Sidebar Client */}
      <SidebarClient 
        activeSection={activeSection}
        onSectionChange={handleSectionChange}
      />
      
      <div className="prediction-container-with-sidebar">
        {/* Contenu principal qui s'adapte selon la section active */}
        {renderContent()}
      </div>  
        
      {/* Footer */}  
      <Footer /> 
    </div>     
  );
};

export default Prediction;   