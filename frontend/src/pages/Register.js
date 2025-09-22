import React, { useState } from 'react';
import './Register.css';

const Register = () => {
  const [formData, setFormData] = useState({
    nom: '',
    prenom: '',
    email: '',
    ville: '',
    pays: '',
    codePostal: '',
    password: '',
    confirmPassword: ''
  });
  
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
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
    return true;
  };
  
const handleSubmit = async (e) => {
  e.preventDefault();
  setError('');
  setSuccess('');

  if (!validateForm()) return;

  setIsLoading(true);

  try {
    const response = await fetch('http://127.0.0.1:5000/api/register', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify(formData)
     }); 

    const data = await response.json();

    if (!response.ok) {
      setError(data.message || 'Erreur serveur');
    } else {
      setSuccess(data.message);
    }
  } catch (err) {
    setError('Impossible de contacter le serveur');
    console.error(err);
  } finally {
    setIsLoading(false);
  } 
};
   
  const handleLogin = () => {
    console.log('Login clicked');
  };
  
  return (
    <div className="register-page">
      {/* Animation de fond simplifiée */}
      <div className="bg-animation">
        <div className="leaf">🌱</div>
        <div className="leaf">🌿</div>
        <div className="leaf">🌱</div>
        <div className="leaf">🌿</div>
        <div className="leaf">🌱</div>
      </div>

      <div className="register-container">
        {/* Section Logo */}
        <div className="logo-section">
          <div className="logo-icon">🚜</div>
          <h1 className="logo-text">AgriConnect</h1>
          <p className="logo-subtitle">Créer votre compte</p>
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

        {/* Formulaire compact */}
        <form onSubmit={handleSubmit} className="compact-form">
          {/* Ligne 1 */}
          <div className="form-row">
            <div className="form-group">
              <label>Nom</label>
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
              <label>Prénom</label>
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

          {/* Ligne 2 */}
          <div className="form-row">
            <div className="form-group">
              <label>Email</label>
              <input 
                type="email" 
                name="email" 
                value={formData.email} 
                onChange={handleChange} 
                placeholder="Email" 
                required 
              />
            </div>
            <div className="form-group">
              <label>Ville</label>
              <input 
                type="text" 
                name="ville" 
                value={formData.ville} 
                onChange={handleChange} 
                placeholder="Ville" 
                required 
              />
            </div>
          </div>

          {/* Ligne 3 */}
          <div className="form-row">
            <div className="form-group">
              <label>Pays</label>
              <input 
                type="text" 
                name="pays" 
                value={formData.pays} 
                onChange={handleChange} 
                placeholder="Pays" 
                required 
              />
            </div>
            <div className="form-group">
              <label>Code postal</label>
              <input 
                type="text" 
                name="codePostal" 
                value={formData.codePostal} 
                onChange={handleChange} 
                placeholder="Code postal" 
                required 
              />
            </div>
          </div>

          {/* Ligne 4 */}
          <div className="form-row">
            <div className="form-group">
              <label>Mot de passe</label>
              <div className="input-wrapper">
                <input 
                  type={showPassword ? 'text' : 'password'} 
                  name="password" 
                  value={formData.password} 
                  onChange={handleChange} 
                  placeholder="Mot de passe" 
                  required 
                />
                <span 
                  className={`password-toggle ${showPassword ? 'fa-eye-slash' : 'fa-eye'}`} 
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? '🙈' : '👁️'}
                </span>
              </div>
            </div>
            <div className="form-group">
              <label>Confirmer</label>
              <div className="input-wrapper">
                <input 
                  type={showConfirmPassword ? 'text' : 'password'} 
                  name="confirmPassword" 
                  value={formData.confirmPassword} 
                  onChange={handleChange} 
                  placeholder="Confirmer" 
                  required 
                />
                <span 
                  className={`password-toggle ${showConfirmPassword ? 'fa-eye-slash' : 'fa-eye'}`} 
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                >
                  {showConfirmPassword ? '🙈' : '👁️'}
                </span>
              </div>
            </div>
          </div>

          {/* Bouton */}
          <button 
            type="submit" 
            className="register-btn"
            disabled={isLoading}
          >
            {isLoading && <div className="loading"></div>}
            <span className="btn-text">
              {isLoading ? 'Inscription...' : "S'inscrire"}
            </span>
          </button>
        </form>

        {/* Lien de connexion */}
        <div className="login-link">
          <span>Déjà un compte ? </span>
          <button type="button" onClick={handleLogin}>
            Se connecter
          </button>
        </div>

        {/* Features compactes */}
        <div className="features-compact">
          <div className="feature-item">📊 Suivi cultures</div>
          <div className="feature-item">🌧️ Météo</div>
          <div className="feature-item">🤖 IA</div>
          <div className="feature-item">📱 Mobile</div>
        </div>
      </div>
    </div>
  );
};

export default Register;  