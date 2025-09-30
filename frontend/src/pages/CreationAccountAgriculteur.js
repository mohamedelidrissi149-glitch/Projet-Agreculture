import React, { useState } from 'react';
import './CreationAccountAgriculteur.css';
import Navbar from '../components/Navbar_Admin';

const CreationAccountAgriculteur = () => {
  const [formData, setFormData] = useState({
    nom: '',
    prenom: '',
    email: '',
    ville: '',
    pays: '',
    codePostal: '',
    password: '', 
    confirmPassword: '',
    dateNaissance: '',
    genre: '',
    telephone: '',
    tailleExploitation: '',
    canalCommunication: '',
    languePreferee: 'francais',
    consentementRGPD: false
  });
     
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Liste complète des pays du monde
  const paysDuMonde = [
    'Afghanistan', 'Afrique du Sud', 'Albanie', 'Algérie', 'Allemagne', 'Andorre', 'Angola', 'Antigua-et-Barbuda',
    'Arabie saoudite', 'Argentine', 'Arménie', 'Australie', 'Autriche', 'Azerbaïdjan', 'Bahamas', 'Bahreïn',
    'Bangladesh', 'Barbade', 'Belgique', 'Belize', 'Bénin', 'Bhoutan', 'Biélorussie', 'Birmanie', 'Bolivie',
    'Bosnie-Herzégovine', 'Botswana', 'Brésil', 'Brunei', 'Bulgarie', 'Burkina Faso', 'Burundi', 'Cambodge',
    'Cameroun', 'Canada', 'Cap-Vert', 'Centrafrique', 'Chili', 'Chine', 'Chypre', 'Colombie', 'Comores',
    'Congo', 'Congo démocratique', 'Corée du Nord', 'Corée du Sud', 'Costa Rica', 'Côte d\'Ivoire', 'Croatie',
    'Cuba', 'Danemark', 'Djibouti', 'Dominique', 'Égypte', 'Émirats arabes unis', 'Équateur', 'Érythrée',
    'Espagne', 'Estonie', 'États-Unis', 'Éthiopie', 'Fidji', 'Finlande', 'France', 'Gabon', 'Gambie', 'Géorgie',
    'Ghana', 'Grèce', 'Grenade', 'Guatemala', 'Guinée', 'Guinée-Bissau', 'Guinée équatoriale', 'Guyana',
    'Haïti', 'Honduras', 'Hongrie', 'Îles Cook', 'Îles Marshall', 'Îles Salomon', 'Inde', 'Indonésie', 'Irak',
    'Iran', 'Irlande', 'Islande', 'Israël', 'Italie', 'Jamaïque', 'Japon', 'Jordanie', 'Kazakhstan', 'Kenya',
    'Kirghizistan', 'Kiribati', 'Kosovo', 'Koweït', 'Laos', 'Lesotho', 'Lettonie', 'Liban', 'Liberia', 'Libye',
    'Liechtenstein', 'Lituanie', 'Luxembourg', 'Macédoine du Nord', 'Madagascar', 'Malaisie', 'Malawi',
    'Maldives', 'Mali', 'Malte', 'Maroc', 'Maurice', 'Mauritanie', 'Mexique', 'Micronésie', 'Moldavie',
    'Monaco', 'Mongolie', 'Monténégro', 'Mozambique', 'Namibie', 'Nauru', 'Népal', 'Nicaragua', 'Niger',
    'Nigeria', 'Niue', 'Norvège', 'Nouvelle-Zélande', 'Oman', 'Ouganda', 'Ouzbékistan', 'Pakistan', 'Palaos',
    'Palestine', 'Panama', 'Papouasie-Nouvelle-Guinée', 'Paraguay', 'Pays-Bas', 'Pérou', 'Philippines', 'Pologne',
    'Portugal', 'Qatar', 'République dominicaine', 'République tchèque', 'Roumanie', 'Royaume-Uni', 'Russie',
    'Rwanda', 'Saint-Kitts-et-Nevis', 'Saint-Vincent-et-les-Grenadines', 'Sainte-Lucie', 'Saint-Marin',
    'Samoa', 'São Tomé-et-Principe', 'Sénégal', 'Serbie', 'Seychelles', 'Sierra Leone', 'Singapour', 'Slovaquie',
    'Slovénie', 'Somalie', 'Soudan', 'Soudan du Sud', 'Sri Lanka', 'Suède', 'Suisse', 'Suriname', 'Syrie',
    'Tadjikistan', 'Tanzanie', 'Tchad', 'Thaïlande', 'Timor oriental', 'Togo', 'Tonga', 'Trinité-et-Tobago',
    'Tunisie', 'Turkménistan', 'Turquie', 'Tuvalu', 'Ukraine', 'Uruguay', 'Vanuatu', 'Vatican', 'Venezuela',
    'Viêt Nam', 'Yémen', 'Zambie', 'Zimbabwe'
  ];

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const validateForm = () => {
    if (formData.password !== formData.confirmPassword) {
      setError('Les mots de passe ne correspondent pas');
      return false;
    }
    if (formData.password.length < 6) {
      setError('Le mot de passe doit contenir au moins 6 caractères');
      return false;
    }
    
    if (!formData.dateNaissance) {
      setError('La date de naissance est requise');
      return false;
    }
    if (!formData.genre) {
      setError('Le genre est requis');
      return false;
    }
    if (!formData.telephone) {
      setError('Le numéro de téléphone est requis');
      return false;
    }
    if (!formData.tailleExploitation) {
      setError('La taille de l\'exploitation est requise');
      return false;
    }
    if (!formData.canalCommunication) {
      setError('Le canal de communication préféré est requis');
      return false;
    }
    if (!formData.consentementRGPD) {
      setError('Vous devez accepter les conditions générales et la politique de confidentialité');
      return false;
    }
    
    return true;
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(''); 
    setSuccess('');
  
    if (!validateForm()) return;

    setIsLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:5000/api/admin/create-agriculteur', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify(formData)
      }); 

      const data = await response.json();

      if (!response.ok) {
        setError(data.message || 'Erreur serveur');
      } else {
        setSuccess('Compte agriculteur créé avec succès !');
        // Reset form
        setFormData({
          nom: '',
          prenom: '',
          email: '',
          ville: '',
          pays: '',
          codePostal: '',
          password: '', 
          confirmPassword: '',
          dateNaissance: '',
          genre: '',
          telephone: '',
          tailleExploitation: '',
          canalCommunication: '',
          languePreferee: 'francais',
          consentementRGPD: false
        });
      }
    } catch (err) {
      setError('Impossible de contacter le serveur');
      console.error(err);
    } finally {
      setIsLoading(false);
    } 
  };
  
  return (
    <div className="admin-page">
      <Navbar />
      
      <div className="creation-page">
        {/* Animation de fond */}
        <div className="bg-animation">
          <div className="leaf">🌱</div>
          <div className="leaf">🌿</div>
          <div className="leaf">🌱</div>
          <div className="leaf">🌿</div>
          <div className="leaf">🌱</div>
        </div>

        <div className="creation-container">
          {/* Section Header Admin */}
          <div className="admin-header">
            <div className="admin-icon">👨‍💼</div>
            <h1 className="admin-title">Panneau Administrateur</h1>
            <p className="admin-subtitle">Créer un compte agriculteur</p>
          </div>

          {/* Messages d'erreur et de succès */}
          {error && (
            <div className="alert alert-error">
              {error} 
            </div>
          )} 
          
          {success && ( 
            <div className="alert alert-success">
              {success} 
            </div>
          )} 

          {/* Formulaire professionnel */}
          <form onSubmit={handleSubmit} className="admin-form">
            
            {/* ========== SECTION INFORMATIONS PERSONNELLES ========== */}
            <div className="form-section">
              <h3 className="section-title">📋 Informations personnelles</h3>
              
              {/* Ligne 1: Nom et Prénom */}
              <div className="form-row">
                <div className="form-group">
                  <label>Nom *</label>
                  <input 
                    type="text" 
                    name="nom" 
                    value={formData.nom} 
                    onChange={handleChange} 
                    placeholder="Nom" 
                    required 
                  />
                </div>
                <div className="form-group">
                  <label>Prénom *</label>
                  <input 
                    type="text" 
                    name="prenom" 
                    value={formData.prenom} 
                    onChange={handleChange} 
                    placeholder="Prénom" 
                    required  
                  /> 
                </div> 
              </div>
    
              {/* Ligne 2: Email et Date de naissance */}
              <div className="form-row">
                <div className="form-group">
                  <label>Email *</label>
                  <input 
                    type="email" 
                    name="email" 
                    value={formData.email}  
                    onChange={handleChange} 
                    placeholder="exemple@email.com" 
                    required  
                  />
                </div>
                <div className="form-group">
                  <label>Date de naissance *</label>
                  <input 
                    type="date" 
                    name="dateNaissance" 
                    value={formData.dateNaissance} 
                    onChange={handleChange} 
                    required 
                  />
                </div>
              </div>

              {/* Ligne 3: Genre et Téléphone */}
              <div className="form-row">
                <div className="form-group">
                  <label>Genre *</label>
                  <select 
                    name="genre" 
                    value={formData.genre} 
                    onChange={handleChange} 
                    required
                  >
                    <option value="">-- Sélectionnez --</option>
                    <option value="homme">Homme</option>
                    <option value="femme">Femme</option>
                    <option value="autre">Autre</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Téléphone *</label>
                  <input 
                    type="tel" 
                    name="telephone" 
                    value={formData.telephone} 
                    onChange={handleChange} 
                    placeholder="+33 6 12 34 56 78" 
                    required 
                  />
                </div>
              </div>
            </div>

            {/* ========== SECTION LOCALISATION ========== */}
            <div className="form-section">
              <h3 className="section-title">📍 Localisation</h3>
              
              {/* Ligne 1: Pays et Ville */}
              <div className="form-row">
                <div className="form-group">
                  <label>Pays *</label>
                  <select 
                    name="pays" 
                    value={formData.pays} 
                    onChange={handleChange} 
                    required
                  >
                    <option value="">-- Choisir un pays --</option>
                    {paysDuMonde.map(pays => (
                      <option key={pays} value={pays}>{pays}</option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label>Ville *</label>
                  <input 
                    type="text" 
                    name="ville" 
                    value={formData.ville} 
                    onChange={handleChange} 
                    placeholder="Nom de la ville" 
                    required 
                  />
                </div>
              </div>

              {/* Ligne 2: Code postal et Langue */}
              <div className="form-row">
                <div className="form-group">
                  <label>Code postal *</label>
                  <input 
                    type="text" 
                    name="codePostal" 
                    value={formData.codePostal} 
                    onChange={handleChange} 
                    placeholder="12345" 
                    required 
                  />
                </div>
                <div className="form-group">
                  <label>Langue préférée *</label>
                  <select 
                    name="languePreferee" 
                    value={formData.languePreferee} 
                    onChange={handleChange} 
                    required
                  >
                    <option value="francais">Français</option>
                    <option value="arabe">العربية</option>
                    <option value="anglais">English</option>
                    <option value="amazigh">Amazigh</option>
                    <option value="espagnol">Español</option>
                    <option value="portugais">Português</option>
                  </select>
                </div>
              </div>
            </div>

            {/* ========== SECTION EXPLOITATION AGRICOLE ========== */}
            <div className="form-section">
              <h3 className="section-title">🚜 Exploitation agricole</h3>
              
              {/* Ligne 1: Taille exploitation et Canal communication */}
              <div className="form-row">
                <div className="form-group">
                  <label>Taille de l'exploitation *</label>
                  <select 
                    name="tailleExploitation" 
                    value={formData.tailleExploitation} 
                    onChange={handleChange} 
                    required
                  >
                    <option value="">-- Sélectionnez --</option>
                    <option value="moins-1ha">Moins de 1 hectare</option>
                    <option value="1-5ha">1 à 5 hectares</option>
                    <option value="5-10ha">5 à 10 hectares</option>
                    <option value="10-20ha">10 à 20 hectares</option>
                    <option value="20-50ha">20 à 50 hectares</option>
                    <option value="50-100ha">50 à 100 hectares</option>
                    <option value="plus-100ha">Plus de 100 hectares</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Canal de communication préféré *</label>
                  <select 
                    name="canalCommunication" 
                    value={formData.canalCommunication} 
                    onChange={handleChange} 
                    required
                  >
                    <option value="">-- Sélectionnez --</option>
                    <option value="email">Email</option>
                    <option value="sms">SMS</option>
                    <option value="whatsapp">WhatsApp</option>
                    <option value="app-mobile">Application mobile</option>
                    <option value="telephone">Téléphone</option>
                  </select>
                </div>
              </div>
            </div>

            {/* ========== SECTION SÉCURITÉ ========== */}
            <div className="form-section">
              <h3 className="section-title">🔐 Sécurité du compte</h3>
              
              {/* Ligne 1: Mots de passe */}
              <div className="form-row">
                <div className="form-group">
                  <label>Mot de passe *</label>
                  <div className="input-wrapper">
                    <input 
                      type={showPassword ? 'text' : 'password'} 
                      name="password" 
                      value={formData.password} 
                      onChange={handleChange} 
                      placeholder="Minimum 6 caractères" 
                      required 
                    />
                    <span 
                      className="password-toggle" 
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? '🙈' : '👁️'}
                    </span>
                  </div>
                </div>
                <div className="form-group">
                  <label>Confirmer le mot de passe *</label>
                  <div className="input-wrapper">
                    <input 
                      type={showConfirmPassword ? 'text' : 'password'} 
                      name="confirmPassword" 
                      value={formData.confirmPassword} 
                      onChange={handleChange} 
                      placeholder="Répéter le mot de passe" 
                      required 
                    />
                    <span 
                      className="password-toggle" 
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    >
                      {showConfirmPassword ? '🙈' : '👁️'}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* ========== SECTION CONSENTEMENT RGPD ========== */}
            <div className="form-section">
              <div className="checkbox-group">
                <input 
                  type="checkbox" 
                  id="consentementRGPD" 
                  name="consentementRGPD" 
                  checked={formData.consentementRGPD} 
                  onChange={handleChange} 
                  required 
                />
                <label htmlFor="consentementRGPD" className="checkbox-label">
                  J'accepte les conditions générales d'utilisation et la politique de confidentialité *
                </label>
              </div>
            </div>

            {/* Bouton de création */}
            <button 
              type="submit" 
              className="admin-create-btn"
              disabled={isLoading}
            >
              {isLoading && <div className="loading"></div>}
              <span className="btn-text">
                {isLoading ? 'Création en cours...' : "Créer le compte agriculteur"}
              </span>
            </button>
          </form>

          {/* Features administrateur */}
          <div className="admin-features"> 
            <div className="feature-item">👨‍💼 Gestion centralisée</div>
            <div className="feature-item">📊 Suivi des comptes</div>
            <div className="feature-item">🔒 Sécurité renforcée</div>
            <div className="feature-item">📧 Notifications automatiques</div>
          </div>
        </div>
      </div>
    </div> 
  );
}; 
   
export default CreationAccountAgriculteur;        