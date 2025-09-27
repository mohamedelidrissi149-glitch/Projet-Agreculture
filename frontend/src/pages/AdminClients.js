import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar_Admin';    
import Footer from '../components/Footer';          
import './AdminClients.css';     
 
const AdminClients = () => {  
  const [clients, setClients] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState(''); // 'create', 'edit', 'delete'
  const [selectedClient, setSelectedClient] = useState(null);
  const [formData, setFormData] = useState({ 
    nom: '', 
    prenom: '',  
    email: '',
    ville: '', 
    pays: '',
    codePostal: '',
    motDePasse: '',
    confirmerMotDePasse: ''
  });  
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [clientsPerPage] = useState(5); 
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(true);

  // URL de base de votre API
  const API_BASE_URL = 'http://localhost:5000/api';

  // Charger les clients depuis l'API
  const fetchClients = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/clients`);
      const data = await response.json();
      
      if (data.success) {
        setClients(data.clients);
      } else {
        console.error('Erreur:', data.message);
        alert('Erreur lors du chargement des clients');
      }
    } catch (error) {
      console.error('Erreur de connexion:', error);
      alert('Erreur de connexion au serveur');
    } finally {
      setLoading(false);
    }
  };

  // Charger les données au démarrage
  useEffect(() => {
    fetchClients();
  }, []);
  
  // Gestion des changements dans les inputs
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    
    // Nettoyer l'erreur quand l'utilisateur tape
    if (errors[name]) {
      setErrors({ ...errors, [name]: '' });
    }
  };

  // Réinitialiser le formulaire
  const resetForm = () => {
    setFormData({
      nom: '',
      prenom: '',
      email: '',
      ville: '',
      pays: '',
      codePostal: '',
      motDePasse: '',
      confirmerMotDePasse: ''
    }); 
    setErrors({});
  }; 

  // Validation du formulaire  
  const validateForm = () => {
    const newErrors = {}; 

    if (!formData.nom.trim()) newErrors.nom = 'Le nom est requis';
    if (!formData.prenom.trim()) newErrors.prenom = 'Le prénom est requis';
    if (!formData.email.trim()) {
      newErrors.email = 'L\'email est requis';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Format d\'email invalide';   
    } 
    if (!formData.ville.trim()) newErrors.ville = 'La ville est requise';
    if (!formData.pays.trim()) newErrors.pays = 'Le pays est requis';
    if (!formData.codePostal.trim()) newErrors.codePostal = 'Le code postal est requis';
    
    if (modalType === 'create' || (modalType === 'edit' && formData.motDePasse)) {
      if (!formData.motDePasse) {
        newErrors.motDePasse = 'Le mot de passe est requis';
      } else if (formData.motDePasse.length < 6) {
        newErrors.motDePasse = 'Le mot de passe doit contenir au moins 6 caractères';
      }
      
      if (!formData.confirmerMotDePasse) {
        newErrors.confirmerMotDePasse = 'Confirmez le mot de passe';
      } else if (formData.motDePasse !== formData.confirmerMotDePasse) {
        newErrors.confirmerMotDePasse = 'Les mots de passe ne correspondent pas';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Ouvrir modal
  const openModal = (type, client = null) => {
    setModalType(type);
    setSelectedClient(client);
    if (client && type === 'edit') {
      setFormData({
        nom: client.nom,
        prenom: client.prenom,
        email: client.email,
        ville: client.ville,
        pays: client.pays,
        codePostal: client.codePostal,
        motDePasse: '',
        confirmerMotDePasse: ''
      });
    } else {
      resetForm();
    }
    setShowModal(true);
  };

  // Fermer modal
  const closeModal = () => {
    setShowModal(false);
    setSelectedClient(null);
    resetForm();
  };

  // Soumettre le formulaire
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    try {
      if (modalType === 'create') {
        const response = await fetch(`${API_BASE_URL}/clients`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData)
        });

        const data = await response.json();
        
        if (data.success) {
          alert('Client créé avec succès !');
          fetchClients(); // Recharger la liste
          closeModal();
        } else {
          alert(`Erreur: ${data.message}`);
        }
      } else if (modalType === 'edit') {
        const response = await fetch(`${API_BASE_URL}/clients/${selectedClient.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData)
        });

        const data = await response.json();
        
        if (data.success) {
          alert('Client modifié avec succès !');
          fetchClients(); // Recharger la liste
          closeModal();
        } else {
          alert(`Erreur: ${data.message}`);
        }
      }
    } catch (error) {
      console.error('Erreur:', error);
      alert('Erreur de connexion au serveur');
    }
  };

  // Supprimer client
  const handleDelete = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/clients/${selectedClient.id}`, {
        method: 'DELETE'
      });

      const data = await response.json();
      
      if (data.success) {
        alert('Client supprimé avec succès !');
        fetchClients(); // Recharger la liste
        closeModal();
      } else {
        alert(`Erreur: ${data.message}`);
      }
    } catch (error) {
      console.error('Erreur:', error);
      alert('Erreur de connexion au serveur');
    }
  };

  // Filtrage des clients
  const filteredClients = clients.filter(client =>
    client.nom.toLowerCase().includes(searchTerm.toLowerCase()) ||
    client.prenom.toLowerCase().includes(searchTerm.toLowerCase()) ||
    client.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    client.ville.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Pagination
  const indexOfLastClient = currentPage * clientsPerPage;
  const indexOfFirstClient = indexOfLastClient - clientsPerPage;
  const currentClients = filteredClients.slice(indexOfFirstClient, indexOfLastClient);
  const totalPages = Math.ceil(filteredClients.length / clientsPerPage);

  const paginate = (pageNumber) => setCurrentPage(pageNumber);

  return ( 
    <div className="admin-layout">
      {/* Navbar fixe */}
      <Navbar onAddClient={() => openModal('create')} />
      
      {/* Contenu principal avec marge pour navbar et footer */}
      <div className="admin-content">
        {/* Search and Stats */}
        <div className="search-stats-section">
          <div className="search-container">
            <div className="search-box">
              <span className="search-icon">🔍</span>
              <input
                type="text"
                placeholder="Rechercher un client..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
              />
            </div>
            <div className="stats-container">
              <div className="stat-card total">
                <div className="stat-number">{clients.length}</div>
                <div className="stat-label">Total Clients</div>
              </div> 
              <div className="stat-card results">
                <div className="stat-number">{filteredClients.length}</div>
                <div className="stat-label">Résultats</div>
              </div>
            </div>
          </div>
        </div>

        {/* Loading state */}
        {loading ? (
          <div className="loading-container">
            <p>Chargement des clients...</p>
          </div>
        ) : (
          /* Table */
          <div className="table-container">
            <div className="table-wrapper">
              <table className="clients-table">
                <thead>
                  <tr>
                    <th>Nom Complet</th>  
                    <th>Email</th>
                    <th>Localisation</th>
                    <th>Actions</th>  
                  </tr> 
                </thead> 
                <tbody>
                  {currentClients.length === 0 ? (
                    <tr>
                      <td colSpan="4" style={{textAlign: 'center', padding: '20px'}}>
                        Aucun client trouvé
                      </td>
                    </tr>
                  ) : (
                    currentClients.map((client, index) => (
                      <tr key={client.id} className={index % 2 === 0 ? 'even' : 'odd'}>
                        <td>
                          <div className="client-info">
                            <div className="client-avatar">
                              {client.prenom.charAt(0)}{client.nom.charAt(0)}
                            </div>
                            <div className="client-name">
                              {client.prenom} {client.nom}
                            </div> 
                          </div>
                        </td>
                        <td className="client-email">{client.email}</td>
                        <td>
                          <div className="client-location">
                            <div>{client.ville}, {client.pays}</div>
                            <div className="postal-code">{client.codePostal}</div>
                          </div>
                        </td>
                        <td>
                          <div className="actions">
                            <button
                              onClick={() => openModal('edit', client)}
                              className="btn-edit"
                              title="Modifier"
                            >
                              ✏️
                            </button>
                            <button
                              onClick={() => openModal('delete', client)}
                              className="btn-delete"
                              title="Supprimer"
                            >
                              🗑️
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="pagination">
                <button
                  onClick={() => paginate(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="pagination-btn"
                >
                  Précédent
                </button>
                
                {[...Array(totalPages)].map((_, i) => (
                  <button
                    key={i + 1}
                    onClick={() => paginate(i + 1)}
                    className={`pagination-btn ${currentPage === i + 1 ? 'active' : ''}`}
                  >
                    {i + 1}
                  </button>
                ))}
                
                <button
                  onClick={() => paginate(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className="pagination-btn"
                >
                  Suivant
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer fixe */}
      <Footer />

      {/* Modal */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>
                {modalType === 'create' && '➕ Nouveau Client'}
                {modalType === 'edit' && '✏️ Modifier Client'}
                {modalType === 'delete' && '🗑️ Supprimer Client'}
              </h2>
              <button onClick={closeModal} className="modal-close">✕</button>
            </div>

            <div className="modal-body">   
              {modalType === 'delete' ? ( 
                <div className="delete-confirmation">
                  <div className="warning-icon">⚠️</div>
                  <p>
                    Êtes-vous sûr de vouloir supprimer le client 
                    <strong> {selectedClient?.prenom} {selectedClient?.nom}</strong> ?
                  </p> 
                  <p className="warning-text">Cette action est irréversible.</p>
                  
                  <div className="modal-actions"> 
                    <button onClick={closeModal} className="btn-secondary">
                      Annuler
                    </button>   
                    <button onClick={handleDelete} className="btn-danger">
                      Supprimer 
                    </button> 
                  </div>
                </div>  
              ) : (
                <form onSubmit={handleSubmit} className="client-form">
                  <div className="form-row">
                    <div className="form-group">
                      <label htmlFor="nom">Nom *</label>
                      <input
                        type="text"
                        id="nom"
                        name="nom"
                        value={formData.nom}
                        onChange={handleInputChange} 
                        className={errors.nom ? 'error' : ''} 
                        placeholder="Entrez le nom"
                      />
                      {errors.nom && <span className="error-message">{errors.nom}</span>}
                    </div>
                    
                    <div className="form-group">
                      <label htmlFor="prenom">Prénom *</label>
                      <input
                        type="text" 
                        id="prenom"
                        name="prenom"
                        value={formData.prenom}
                        onChange={handleInputChange}
                        className={errors.prenom ? 'error' : ''}
                        placeholder="Entrez le prénom"
                      />
                      {errors.prenom && <span className="error-message">{errors.prenom}</span>}
                    </div>
                  </div>

                  <div className="form-group">
                    <label htmlFor="email">Email *</label>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      className={errors.email ? 'error' : ''}
                      placeholder="exemple@email.com"
                    />
                    {errors.email && <span className="error-message">{errors.email}</span>}
                  </div> 

                  <div className="form-row">
                    <div className="form-group">
                      <label htmlFor="ville">Ville *</label>
                      <input
                        type="text"
                        id="ville"
                        name="ville"
                        value={formData.ville}
                        onChange={handleInputChange}
                        className={errors.ville ? 'error' : ''}
                        placeholder="Entrez la ville"
                      />
                      {errors.ville && <span className="error-message">{errors.ville}</span>}
                    </div>
                    
                    <div className="form-group">
                      <label htmlFor="pays">Pays *</label>
                      <input
                        type="text"
                        id="pays"
                        name="pays"
                        value={formData.pays}
                        onChange={handleInputChange}
                        className={errors.pays ? 'error' : ''}
                        placeholder="Entrez le pays"
                      />
                      {errors.pays && <span className="error-message">{errors.pays}</span>}
                    </div>
                  </div>

                  <div className="form-group">
                    <label htmlFor="codePostal">Code Postal *</label>
                    <input
                      type="text"
                      id="codePostal"
                      name="codePostal"
                      value={formData.codePostal}
                      onChange={handleInputChange}
                      className={errors.codePostal ? 'error' : ''} 
                      placeholder="Entrez le code postal"
                    />
                    {errors.codePostal && <span className="error-message">{errors.codePostal}</span>}
                  </div>

                  <div className="form-group">
                    <label htmlFor="motDePasse">
                      Mot de passe {modalType === 'create' ? '*' : '(laisser vide pour ne pas changer)'}
                    </label>
                    <input
                      type="password"
                      id="motDePasse"
                      name="motDePasse"
                      value={formData.motDePasse}
                      onChange={handleInputChange}
                      className={errors.motDePasse ? 'error' : ''}
                      placeholder="Entrez le mot de passe"
                    />
                    {errors.motDePasse && <span className="error-message">{errors.motDePasse}</span>}
                  </div>

                  <div className="form-group">
                    <label htmlFor="confirmerMotDePasse">
                      Confirmer le mot de passe {modalType === 'create' ? '*' : ''}
                    </label>
                    <input
                      type="password"
                      id="confirmerMotDePasse"
                      name="confirmerMotDePasse" 
                      value={formData.confirmerMotDePasse}
                      onChange={handleInputChange}
                      className={errors.confirmerMotDePasse ? 'error' : ''}
                      placeholder="Confirmez le mot de passe" 
                    /> 
                    {errors.confirmerMotDePasse && <span className="error-message">{errors.confirmerMotDePasse}</span>}
                  </div> 
        
                  <div className="modal-actions">
                    <button type="button" onClick={closeModal} className="btn-secondary">
                      Annuler
                    </button>
                    <button type="submit" className="btn-primary">
                      {modalType === 'create' ? 'Créer' : 'Modifier'}
                    </button>
                  </div>
                </form>  
              )} 
            </div>   
          </div>
        </div>
      )} 
    </div>
  );    
};
 
export default AdminClients;  