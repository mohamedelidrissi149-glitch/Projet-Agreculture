import React, { useState, useEffect } from 'react';
import './HistoriquePredictionsTotal.css';
import Navbar from '../components/Navbar_Admin';

const HistoriquePredictionsTotal = () => {
  const [historique, setHistorique] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [predictionsPerPage] = useState(10);
  const [loading, setLoading] = useState(true);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteType, setDeleteType] = useState('');
  const [selectedPrediction, setSelectedPrediction] = useState(null);

  // Récupération des données depuis l'API
  useEffect(() => {
    const fetchHistorique = async () => {
      try {
        setLoading(true);
        console.log('🚀 Chargement des prédictions...');
        
        const response = await fetch('http://localhost:5000/api/predictions');
        const result = await response.json();
        
        console.log('📊 Réponse API:', result);
        
        if (result.success && result.data) {
          setHistorique(result.data);
          console.log(`✅ ${result.data.length} prédictions chargées`);
        } else {
          console.error('❌ Erreur API:', result.error);
          setHistorique([]);
        }
      } catch (error) {
        console.error('❌ Erreur lors du chargement des prédictions:', error);
        setHistorique([]);
      } finally {
        setLoading(false);
      }
    };
    
    fetchHistorique();
  }, []);

  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('fr-FR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (error) {
      return 'Date invalide';
    }
  };

  const formatCulture = (culture) => {
    const cultures = {
      'apple': 'Pomme 🍎',
      'rice': 'Riz 🌾',
      'wheat': 'Blé 🌾',
      'corn': 'Maïs 🌽',
      'kidneybeans': 'Haricots 🫘',
      'tomato': 'Tomate 🍅'
    };
    return cultures[culture] || culture;
  };

  // Filtrage des prédictions
  const filteredPredictions = historique.filter(prediction => {
    const searchLower = searchTerm.toLowerCase();
    return (
      prediction.email_agriculteur.toLowerCase().includes(searchLower) ||
      prediction.nom_agriculteur.toLowerCase().includes(searchLower) ||
      prediction.culture_recommandee.toLowerCase().includes(searchLower)
    );
  });

  // Pagination
  const indexOfLastPrediction = currentPage * predictionsPerPage;
  const indexOfFirstPrediction = indexOfLastPrediction - predictionsPerPage;
  const currentPredictions = filteredPredictions.slice(indexOfFirstPrediction, indexOfLastPrediction);
  const totalPages = Math.ceil(filteredPredictions.length / predictionsPerPage);

  const paginate = (pageNumber) => setCurrentPage(pageNumber);

  const openDeleteModal = (type, prediction = null) => {
    setDeleteType(type);
    setSelectedPrediction(prediction);
    setShowDeleteModal(true);
  };

  const closeDeleteModal = () => {
    setShowDeleteModal(false);
    setSelectedPrediction(null);
    setDeleteType('');
  };

  // Suppression d'une prédiction unique - CORRIGÉ
  const handleDeleteSingle = async () => {
    if (!selectedPrediction) {
      alert('Erreur: Aucune prédiction sélectionnée');
      return;
    }

    try {
      console.log('🗑️ Suppression de la prédiction:', selectedPrediction);
      
      const response = await fetch('http://localhost:5000/api/predictions/delete', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email_agriculteur: selectedPrediction.email_agriculteur,
          azote_n: selectedPrediction.azote_n || selectedPrediction.azote, // Support des deux formats
          phosphore_p: selectedPrediction.phosphore_p || selectedPrediction.phosphore // Support des deux formats
        })
      });

      const result = await response.json();
      console.log('📋 Résultat suppression:', result);

      if (result.success) {
        // Mise à jour de l'état local - recherche plus flexible
        const updatedHistorique = historique.filter(p => {
          const sameEmail = p.email_agriculteur === selectedPrediction.email_agriculteur;
          const sameAzote = (p.azote === selectedPrediction.azote) || (p.azote_n === selectedPrediction.azote_n);
          const samePhosphore = (p.phosphore === selectedPrediction.phosphore) || (p.phosphore_p === selectedPrediction.phosphore_p);
          return !(sameEmail && sameAzote && samePhosphore);
        });
        setHistorique(updatedHistorique);
        alert('✅ Prédiction supprimée avec succès !');
        closeDeleteModal();
      } else {
        alert(`❌ Erreur lors de la suppression: ${result.error}`);
      }
    } catch (error) {
      console.error('❌ Erreur lors de la suppression:', error);
      alert('❌ Erreur lors de la suppression');
    }
  };

  // Suppression de tout l'historique
  const handleDeleteAll = async () => {
    try {
      console.log('🗑️ Suppression de tout l\'historique...');
      
      const response = await fetch('http://localhost:5000/api/predictions/clear', {
        method: 'DELETE'
      });

      const result = await response.json();
      console.log('📋 Résultat suppression complète:', result);

      if (result.success) {
        setHistorique([]);
        alert(`✅ Historique vidé avec succès ! (${result.deleted_count} éléments supprimés)`);
        closeDeleteModal();
      } else {
        alert(`❌ Erreur lors de la suppression: ${result.error}`);
      }
    } catch (error) {
      console.error('❌ Erreur lors de la suppression:', error);
      alert('❌ Erreur lors de la suppression');
    }
  };

  return (
    <div className="historique-layout">
      <Navbar />
      <div className="historique-content">
        {/* Header */}
        <div className="header-section">
          <h1 className="page-title">📊 Historique des Prédictions Agricoles</h1>
          <button 
            onClick={() => openDeleteModal('all')}
            className="btn-clear-all"
            disabled={historique.length === 0}
          >
            🗑️ Vider l'Historique
          </button>
        </div>

        {/* Recherche & Stats */}
        <div className="search-stats-section">
          <div className="search-container">
            <div className="search-box">
              <span className="search-icon">🔍</span>
              <input
                type="text"
                placeholder="Rechercher par agriculteur, email ou culture..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
              />
            </div>
            <div className="stats-container">
              <div className="stat-card total">
                <div className="stat-number">{historique.length}</div>
                <div className="stat-label">Total Prédictions</div>
              </div>
              <div className="stat-card results">
                <div className="stat-number">{filteredPredictions.length}</div>
                <div className="stat-label">Résultats Trouvés</div>
              </div>
            </div>
          </div>
        </div>

        {/* Table */}
        {loading ? (
          <div className="loading-container">
            <div className="loading-spinner">🔄</div>
            <p>Chargement de l'historique des prédictions...</p>
          </div>
        ) : (
          <div className="table-container">
            <table className="predictions-table">
              <thead>
                <tr>
                  <th>Email Agriculteur</th>
                  <th>Nom Agriculteur</th>
                  <th>Azote (N)</th>
                  <th>Phosphore (P)</th>
                  <th>Potassium (K)</th>
                  <th>Température (°C)</th>
                  <th>Humidité (%)</th>
                  <th>pH</th>
                  <th>Pluie Mensuelle (mm)</th>
                  <th>Pluie Annuelle (mm)</th>
                  <th>Besoin Irrigation</th>
                  <th>Culture Recommandée</th>
                  <th>Date Prédiction</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {currentPredictions.length === 0 ? (
                  <tr>
                    <td colSpan="14" className="no-data">
                      📭 Aucune prédiction trouvée
                    </td>
                  </tr>
                ) : (
                  currentPredictions.map((prediction, index) => (
                    <tr key={`${prediction.email_agriculteur}-${prediction.azote}-${prediction.phosphore}-${index}`} 
                        className={index % 2 === 0 ? 'even' : 'odd'}>
                      <td>{prediction.email_agriculteur}</td>
                      <td>{prediction.nom_agriculteur}</td>
                      <td>{prediction.azote}</td>
                      <td>{prediction.phosphore}</td>
                      <td>{prediction.potassium}</td>
                      <td>{prediction.temperature_celsius}°C</td>
                      <td>{prediction.humidite_pourcentage}%</td>
                      <td>{prediction.ph}</td>
                      <td>{prediction.pluie_mensuelle_mm}mm</td>
                      <td>{prediction.pluie_annuelle_mm}mm</td>
                      <td>{prediction.besoin_irrigation.includes('Oui') ? '💧 Oui' : '🚫 Non'}</td>
                      <td>{formatCulture(prediction.culture_recommandee)}</td>
                      <td>{formatDate(prediction.date_prediction)}</td>
                      <td>
                        <button 
                          onClick={() => openDeleteModal('single', prediction)}
                          className="btn-delete"
                        >
                          🗑️
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="pagination">
                <button 
                  onClick={() => paginate(currentPage - 1)} 
                  disabled={currentPage === 1}
                >
                  ← Précédent
                </button>
                {[...Array(totalPages)].map((_, i) => (
                  <button 
                    key={i + 1} 
                    onClick={() => paginate(i + 1)} 
                    className={currentPage === i + 1 ? 'active' : ''}
                  >
                    {i + 1}
                  </button>
                ))}
                <button 
                  onClick={() => paginate(currentPage + 1)} 
                  disabled={currentPage === totalPages}
                >
                  Suivant →
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Modal Suppression */}
      {showDeleteModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h2>{deleteType === 'single' ? '🗑️ Supprimer la Prédiction' : '🗑️ Vider l\'Historique'}</h2>
            {deleteType === 'single' ? (
              <div>
                <p>Supprimer la prédiction de <strong>{selectedPrediction?.nom_agriculteur}</strong> ?</p>
                <div className="prediction-details">
                  <p><strong>Email:</strong> {selectedPrediction?.email_agriculteur}</p>
                  <p><strong>Culture:</strong> {formatCulture(selectedPrediction?.culture_recommandee)}</p>
                  <p><strong>Azote:</strong> {selectedPrediction?.azote}</p>
                  <p><strong>Phosphore:</strong> {selectedPrediction?.phosphore}</p>
                </div>
              </div>
            ) : (
              <p>Supprimer tout l'historique ({historique.length} prédiction(s)) ?</p>
            )}
            <div className="modal-actions">
              <button onClick={closeDeleteModal} className="btn-cancel">
                Annuler
              </button>
              <button 
                onClick={deleteType === 'single' ? handleDeleteSingle : handleDeleteAll}
                className="btn-confirm"
              >
                {deleteType === 'single' ? 'Supprimer' : 'Vider l\'Historique'}
              </button>
            </div>
          </div> 
        </div>
      )}
    </div>
  );
};

export default HistoriquePredictionsTotal;  