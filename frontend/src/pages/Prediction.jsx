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
  faTrash, faDroplet, faCalculator, faCalendarAlt, faSync 
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
  const [isHistoryLoading, setIsHistoryLoading] = useState(false);
  
  // État pour gérer le sidebar
  const [activeSection, setActiveSection] = useState('prediction');
  
  const navigate = useNavigate();

  // Historique récupéré depuis la base de données
  const [historique, setHistorique] = useState([]);

  // Calcul des statistiques
  const totalAnalyses = historique.length;
  const irrigationOui = historique.filter(item => item.besoin_irrigation === "Oui").length;
  const irrigationNon = historique.filter(item => item.besoin_irrigation === "Non").length;
  const pourcentageIrrigation = totalAnalyses > 0 ? Math.round((irrigationOui / totalAnalyses) * 100) : 0;

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
      
      // Charger l'historique au démarrage
      loadUserPredictions();
    } catch (error) {
      console.log('Erreur parsing user data');
      localStorage.removeItem('authToken');
      localStorage.removeItem('userData');
      navigate('/login');
    }
  }, [navigate]);

  // Fonction pour charger l'historique depuis la base de données
  const loadUserPredictions = async () => {
    setIsHistoryLoading(true);
    try {
      const token = localStorage.getItem('authToken');
      
      if (!token) {
        console.log('Token manquant');
        return;
      }

      const response = await fetch("http://localhost:5000/api/get-user-predictions", {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        },
      });

      if (response.status === 401) {
        console.log('Token expiré');
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
        navigate('/login');
        return;
      }

      const data = await response.json();
      
      if (data.success) {
        setHistorique(data.predictions || []);
        console.log(`Historique chargé: ${data.predictions.length} prédictions`);
      } else {
        console.error('Erreur chargement historique:', data.error);
        setHistorique([]); // En cas d'erreur, garder un tableau vide
      }
    } catch (error) {
      console.error('Erreur réseau historique:', error);
      setHistorique([]); // En cas d'erreur, garder un tableau vide
    } finally {
      setIsHistoryLoading(false);
    }
  };

  // Gestionnaire pour changer de section
  const handleSectionChange = (section) => {
    setActiveSection(section);
    console.log('Section changée vers:', section);
    
    // Recharger l'historique si on va sur cette section
    if (section === 'historique') {
      loadUserPredictions();
    }
  }; 

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // Fonction pour supprimer une entrée de l'historique
  const handleDelete = async (predictionId) => {
    try {
      const token = localStorage.getItem('authToken');
      
      if (!token) {
        console.log('Token manquant pour suppression');
        return;
      }

      const response = await fetch(`http://localhost:5000/api/delete-prediction/${predictionId}`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        },
      });

      if (response.status === 401) {
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
        navigate('/login');
        return;
      }

      const data = await response.json();
      
      if (data.success) {
        // Recharger l'historique après suppression
        loadUserPredictions();
        console.log('Entrée supprimée avec succès');
      } else {
        console.error('Erreur suppression:', data.error);
      }
    } catch (error) {
      console.error('Erreur réseau suppression:', error);
    }
  };

  // Fonction pour obtenir les détails de la culture - CORRIGÉE
  const getCropDetails = (cropName) => {
    // VÉRIFICATION CRUCIALE pour éviter l'erreur
    if (!cropName || typeof cropName !== 'string') {
      return { 
        icon: faSeedling, 
        emoji: '🌱', 
        color: '#4caf50',
        description: 'Culture à déterminer'
      };
    }

    const cropData = {
      'pomme': { 
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

  // Fonction pour sauvegarder une prédiction dans la base
  const savePredictionToDatabase = async (irrigationPrediction, cropPrediction) => {
    try {
      const token = localStorage.getItem('authToken');
      
      if (!token) {
        console.log('Token manquant pour sauvegarde');
        return;
      }

      const saveData = {
        ...formData,
        irrigation_prediction: irrigationPrediction,
        crop_recommendation: cropPrediction
      };

      const response = await fetch("http://localhost:5000/api/save-prediction", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify(saveData),
      });

      const data = await response.json();
      
      if (data.success) {
        console.log('Prédiction sauvegardée:', data.prediction_id);
        // Recharger l'historique après sauvegarde
        loadUserPredictions();
      } else {
        console.error('Erreur sauvegarde:', data.error);
      }
    } catch (error) {
      console.error('Erreur réseau sauvegarde:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    // Reset des états d'erreur
    setErrorMsg(null);
    setCropErrorMsg(null);
    setGeminiErrorMsg(null);
    
    try {
      const token = localStorage.getItem('authToken');
      
      if (!token) {
        setErrorMsg("Session expirée, veuillez vous reconnecter");
        navigate('/login');
        return;
      }
       
      console.log('Envoi de la prédiction...');
      
      let irrigationPrediction = null;
      let cropPrediction = null;
      
      // Appel pour la prédiction d'irrigation
      try {
        const irrigationResponse = await fetch("http://localhost:5000/api/predict", {
          method: "POST",
          headers: { 
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
          },
          body: JSON.stringify(formData),
        });
        
        const irrigationData = await irrigationResponse.json();
        
        if (irrigationResponse.status === 401) {
          setErrorMsg("Session expirée, veuillez vous reconnecter");
          localStorage.removeItem('authToken');
          localStorage.removeItem('userData');
          navigate('/login');
          return;
        }
        
        if (irrigationData.success && irrigationData.prediction) {
          setPrediction(irrigationData.prediction);
          irrigationPrediction = irrigationData.prediction;
          console.log('Prédiction irrigation reçue:', irrigationData.prediction);
        } else {
          setPrediction(null);
          setErrorMsg(irrigationData.error || "Erreur serveur irrigation");
          console.log('Erreur prédiction irrigation:', irrigationData.error);
        }
        
      } catch (error) {
        setPrediction(null);
        setErrorMsg("Erreur lors de la prédiction d'irrigation");
        console.error('Erreur prédiction irrigation:', error);
      }
      
      // Appel pour la recommandation de culture
      try {
        const cropResponse = await fetch("http://localhost:5000/api/crop-recommendation", {
          method: "POST",
          headers: { 
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
          },
          body: JSON.stringify(formData),
        });
        
        if (cropResponse.status === 404) {
          setCropErrorMsg("Service de recommandation de culture temporairement indisponible");
          setCropRecommendation(null);
          console.log('Endpoint crop-recommendation non trouvé (404)');
        } else {
          const cropData = await cropResponse.json();
          
          if (cropData.success && cropData.crop) {
            setCropRecommendation(cropData.crop);
            cropPrediction = cropData.crop;
            console.log('Recommandation culture reçue:', cropData.crop);
          } else {
            setCropRecommendation(null);
            setCropErrorMsg(cropData.error || "Erreur recommandation culture");
            console.log('Erreur recommandation culture:', cropData.error);
          }
        }
        
      } catch (error) {
        setCropRecommendation(null);
        setCropErrorMsg("Service de recommandation de culture indisponible");
        console.error('Erreur recommandation culture:', error);
      }

      // Appel pour les conseils Gemini LLM
      if (irrigationPrediction || cropPrediction) {
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
              irrigationPrediction: irrigationPrediction,
              cropRecommendation: cropPrediction
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

      // SAUVEGARDER dans la base de données si au moins une prédiction a réussi
      if (irrigationPrediction || cropPrediction) {
        await savePredictionToDatabase(irrigationPrediction, cropPrediction);
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
    { title: "Économies", text: "Optimisation des ressources en eau", icon: faSave },
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
              <p>Consultez vos analyses précédentes et les statistiques détaillées</p>
              <button 
                onClick={loadUserPredictions} 
                className="prediction-refresh-btn"
                disabled={isHistoryLoading}
              >
                <FontAwesomeIcon icon={faSync} spin={isHistoryLoading} />
                {isHistoryLoading ? 'Actualisation...' : 'Actualiser'}
              </button>
            </div>

            {/* Cartes de statistiques */}
            <div className="prediction-stats-grid">
              <div className="prediction-stats-card prediction-stats-total">
                <div className="prediction-stats-icon">
                  <FontAwesomeIcon icon={faCalculator} />
                </div>
                <div className="prediction-stats-content">
                  <h3>{totalAnalyses}</h3>
                  <p>Total des Analyses</p>
                </div>
              </div>

              <div className="prediction-stats-card prediction-stats-irrigation">
                <div className="prediction-stats-icon">
                  <FontAwesomeIcon icon={faDroplet} />
                </div>
                <div className="prediction-stats-content">
                  <h3>{irrigationOui}</h3>   
                  <p>Besoin d'Irrigation</p> 
                  <small>{pourcentageIrrigation}% des analyses</small>
                </div>
              </div>

              <div className="prediction-stats-card prediction-stats-no-irrigation">
                <div className="prediction-stats-icon">
                  <FontAwesomeIcon icon={faSeedling} />
                </div>  
                <div className="prediction-stats-content">
                  <h3>{irrigationNon}</h3>
                  <p>Pas d'Irrigation</p>
                  <small>{100 - pourcentageIrrigation}% des analyses</small>
                </div>
              </div>

              <div className="prediction-stats-card prediction-stats-date">
                <div className="prediction-stats-icon">
                  <FontAwesomeIcon icon={faCalendarAlt} />
                </div>
                <div className="prediction-stats-content">
                  <h3>{historique.length > 0 ? historique[0].date : 'N/A'}</h3>
                  <p>Dernière Analyse</p>
                  <small>Analyse la plus récente</small>
                </div>
              </div> 
            </div>

            {/* Tableau historique */}
            <div className="prediction-history-table-container">
              <div className="prediction-table-header">
                <h3>📋 Détail des Analyses Complètes</h3>
                <p>Toutes vos prédictions agricoles avec données complètes</p>
              </div>

              {isHistoryLoading ? (
                <div className="prediction-loading-container">
                  <div className="prediction-result-card">
                    <div className="prediction-result-icon">⏳</div>
                    <div className="prediction-result-text">Chargement de l'historique...</div>
                    <div className="prediction-result-description">
                      Récupération des données depuis la base de données.
                    </div>
                  </div>
                </div>
              ) : historique && historique.length > 0 ? (
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
                          <td><span className="prediction-value">{item.pluie_mensuelle}</span></td>
                          <td><span className="prediction-value">{item.pluie_annuelle}</span></td>
                          <td>
                            <span className={`prediction-irrigation-badge ${item.besoin_irrigation === "Oui" ? "prediction-irrigation-yes" : "prediction-irrigation-no"}`}>
                              <FontAwesomeIcon icon={item.besoin_irrigation === "Oui" ? faDroplet : faSeedling} />
                              {item.besoin_irrigation}
                            </span>
                          </td>
                          <td>
                            <span className="prediction-crop-badge">
                              {getCropDetails(item.culture_recommandee || "").emoji}
                              {item.culture_recommandee || "Non définie"}
                            </span>
                          </td>
                          <td>
                            <button
                              onClick={() => handleDelete(item.id)}
                              className="prediction-delete-btn"
                              title="Supprimer cette entrée"
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
                  <FontAwesomeIcon icon={faChartLine} className="prediction-placeholder-icon"/>
                  <h3>Historique vide</h3>
                  <p>Vous n'avez encore aucune prédiction enregistrée.</p>
                  <p>Effectuez votre première analyse pour voir les données ici.</p>
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
                    <p><strong>Analyses effectuées:</strong> {totalAnalyses}</p>
                    <p><strong>Dernière connexion:</strong> {new Date().toLocaleDateString()}</p>
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
                  Entrez les paramètres pour obtenir des recommandations d'irrigation, de culture et des conseils IA
                </p>
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
                    {isLoading ? 'Analyse en cours...' : 'Analyser avec IA'}
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
                <FontAwesomeIcon icon={faChartLine}/> Résultats ML
              </h2>

              {isLoading ? (
                <div className="prediction-loading-container">
                  <div className="prediction-result-card">
                    <div className="prediction-result-icon">⏳</div>
                    <div className="prediction-result-text">Analyse en cours...</div>
                    <div className="prediction-result-description">
                      Veuillez patienter pendant l'analyse des données.
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
                        </div>
                      ) : (
                        <div className="prediction-result-card">
                          <div className="prediction-result-icon">🤖</div>
                          <div className="prediction-result-text">En attente d'analyse</div>
                          <div className="prediction-result-description">
                            Remplissez le formulaire pour obtenir une recommandation.
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