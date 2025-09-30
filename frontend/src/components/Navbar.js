import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSeedling, faSignOutAlt } from '@fortawesome/free-solid-svg-icons';
import './Navbar.css';

const Navbar = () => {
  const navigate = useNavigate();
  
  const handleLogout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userData');
    sessionStorage.setItem('fromLogout', 'true');
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        {/* Logo Section */}
        <div className="navbar-logo">
          <FontAwesomeIcon icon={faSeedling} className="navbar-logo-icon"/>
          <span className="navbar-logo-text">AgriPredict</span>
        </div>

        {/* Navigation Links */}  
        <div className="navbar-menu">
                
          <Link to="" className="navbar-link">Accueil</Link>
          <Link to="" className="navbar-link">Clients</Link>
          <Link to="" className="navbar-link">Ajouter Client</Link>
          <Link to="" className="navbar-link">À propos</Link>  
          <Link to="" className="navbar-link">Contact</Link>
                   
          
          {/* Logout Button */} 
          <button className="navbar-logout-btn" onClick={handleLogout}>
            <FontAwesomeIcon icon={faSignOutAlt} />
            Déconnexion
          </button>
        </div>
      </div>   
    </nav> 
  );
};

export default Navbar;  