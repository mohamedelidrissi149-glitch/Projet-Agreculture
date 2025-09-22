// src/pages/Login.js
import React, { useState, useEffect } from 'react';
import './Login.css';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const navigate = useNavigate();

  // ⭐ VÉRIFICATION au chargement - Support multi-rôles
  useEffect(() => {
    const checkExistingAuth = async () => {
      const token = localStorage.getItem('authToken');
      const isFromLogout = sessionStorage.getItem('fromLogout');
      
      // Si on vient de la déconnexion, nettoyer et ne pas rediriger
      if (isFromLogout) {
        sessionStorage.removeItem('fromLogout');
        return;
      }
      
      if (token) {
        try {
          const response = await fetch('http://localhost:5000/api/auth/verify', {
            headers: { 'Authorization': `Bearer ${token}` }
          });
          
          if (response.ok) {
            const data = await response.json();
            if (data.success && data.user) {
              // ⭐ REDIRECTION selon le rôle
              if (data.user.role === 'admin') {
                navigate('/AdminClients');
              } else if (data.user.role === 'user') {
                navigate('/Prediction');
              }
            }
          } else {
            // Token invalide, le supprimer
            localStorage.removeItem('authToken');
            localStorage.removeItem('userData');
          }
        } catch (error) {
          // Erreur, supprimer le token
          localStorage.removeItem('authToken');
          localStorage.removeItem('userData');
        }
      }
    };
    
    checkExistingAuth();
  }, [navigate]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError('');
  };

  const togglePassword = () => setShowPassword(!showPassword);

  const handleSubmit = async () => {
    setIsLoading(true); 
    setError(''); 
 
    try {
      const response = await fetch('http://localhost:5000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json', 
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password
        })
      });

      const data = await response.json();

      if (data.success) {
        // ⭐ SAUVEGARDER le token et les données utilisateur
        localStorage.setItem('authToken', data.token);
        localStorage.setItem('userData', JSON.stringify(data.user));
        
        // ⭐ REDIRECTION selon le rôle utilisateur
        if (data.user.role === 'admin') {
          console.log('Redirection admin vers AdminClients');
          navigate('/AdminClients');  
        } else if (data.user.role === 'user') {
          console.log('Redirection user vers Prediction');
          navigate('/Prediction');
        } else { 
          setError('Rôle utilisateur non reconnu');
        }
      } else {
        setError(data.message || 'Erreur de connexion');
      }   
    } catch (error) {
      console.error('Erreur:', error);
      setError('Erreur de connexion au serveur');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleForgotPassword = () => console.log('Forgot password clicked');

  const handleRegister = () => navigate('/register');
 
  return (
    <div className="login-page">
      <div className="bg-animation">
        {[...Array(9)].map((_, i) => (
          <div key={i} className="leaf">
            <i className={`fas ${i % 3 === 0 ? 'fa-leaf' : i % 3 === 1 ? 'fa-seedling' : 'fa-tree'}`}></i>
          </div>
        ))}
      </div>

      <div className="login-container">
        <div className="logo-section">
          <div className="logo-icon"><i className="fas fa-tractor"></i></div>
          <h1 className="logo-text">AgriConnect</h1>
          <p className="logo-subtitle">Votre partenaire numérique agricole</p>
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        <div className="login-form">
          <div className="form-group">
            <label>Email</label>
            <div className="input-wrapper">
              <i className="fas fa-user input-icon"></i>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="Entrez votre email"
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label>Mot de passe</label>
            <div className="input-wrapper">
              <i className="fas fa-lock input-icon"></i>
              <input
                type={showPassword ? 'text' : 'password'}
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                placeholder="Entrez votre mot de passe"
                required
              /> 
              <button type="button" className="password-toggle" onClick={togglePassword}>
                <i className={`fas ${showPassword ? 'fa-eye-slash' : 'fa-eye'}`}></i>
              </button>
            </div>
          </div>

          <button 
            type="button" 
            className="login-btn" 
            onClick={handleSubmit} 
            disabled={isLoading || !formData.email || !formData.password}
          >
            {isLoading && <div className="loading"></div>}
            <span className="btn-text">{isLoading ? 'Connexion...' : 'Se connecter'}</span>
          </button>
        </div>

        <div className="forgot-password">
          <button type="button" onClick={handleForgotPassword}>Mot de passe oublié ?</button>
        </div>

        <div className="divider"><span>Nouveau sur AgriConnect ?</span></div>

        <div className="register-link">
          Pas encore de compte ?{' '} 
          <button type="button" onClick={handleRegister}>Créer un compte</button>
        </div>
      </div>
    </div>
  );  
};

export default Login;  
    