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
          <Link to="/Historique" className="navbar-link">Historique</Link> 
          <Link to="/GestionAgriculteurs" className="navbar-link">Gestion des Agriculteurs</Link>
          <Link to="/clients" className="navbar-link">Clients</Link>
          <Link to="/admin/create-agriculteur" className="navbar-link">Ajouter Agriculteur</Link> 
          <Link to="/about" className="navbar-link">À propos</Link> 
           
          
          
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