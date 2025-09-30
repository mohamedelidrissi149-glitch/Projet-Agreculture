import React, { useState } from 'react';
import './SidebarClient.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faHistory,
  faUser,
  faBars,
  faTimes,
  faChevronRight,
  faLeaf,
  faPlusCircle,
  faHome
} from '@fortawesome/free-solid-svg-icons';

const SidebarClient = ({ activeSection, onSectionChange }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isVisible, setIsVisible] = useState(true);

  const toggleSidebar = () => setIsCollapsed(!isCollapsed);
  const toggleVisibility = () => setIsVisible(!isVisible);

  // Menu principal
  const menuItems = [
    { id: 'accueil', label: 'Accueil', icon: faHome, description: 'Page d’accueil' },
    { id: 'historique', label: 'Historique', icon: faHistory, description: 'Voir vos historiques' },
    { id: 'profil', label: 'Profil', icon: faUser, description: 'Gérer votre profil' },
     
  ];

  const handleItemClick = (itemId) => {
    if (onSectionChange) onSectionChange(itemId);
  };

  // Si masqué → bouton hamburger
  if (!isVisible) {
    return (
      <div className="sidebar-toggle-button" onClick={toggleVisibility}>
        <FontAwesomeIcon icon={faBars} />
      </div>
    );
  }

  return (
    <div className={`sidebar-client ${isCollapsed ? 'collapsed' : ''}`}>
      {/* Header */}
      <div className="sidebar-header">
        <div className="sidebar-brand">
          <FontAwesomeIcon icon={faLeaf} className="sidebar-brand-icon" />
          {!isCollapsed && <span className="sidebar-brand-text">AgriPredict</span>}
        </div>
        <div className="sidebar-controls">
          <button
            className="sidebar-collapse-btn"
            onClick={toggleSidebar}
            title={isCollapsed ? 'Développer' : 'Réduire'}
          >
            <FontAwesomeIcon icon={isCollapsed ? faChevronRight : faTimes} />
          </button>
          <button
            className="sidebar-hide-btn"
            onClick={toggleVisibility}
            title="Masquer"
          >
            <FontAwesomeIcon icon={faBars} />
          </button>
        </div>
      </div>

      {/* Menu */}
      <div className="sidebar-menu">
        {!isCollapsed && <div className="sidebar-section-title">Navigation</div>}
        {menuItems.map((item) => (
          <button
            key={item.id}
            className={`sidebar-menu-item ${activeSection === item.id ? 'active' : ''}`}
            onClick={() => handleItemClick(item.id)}
            title={isCollapsed ? item.label : ''}
          >
            <div className="sidebar-item-icon">
              <FontAwesomeIcon icon={item.icon} />
            </div>
            {!isCollapsed && (
              <div className="sidebar-item-content">
                <span className="sidebar-item-label">{item.label}</span>
                <span className="sidebar-item-description">{item.description}</span>
              </div>
            )}
            {!isCollapsed && (
              <div className="sidebar-item-arrow">
                <FontAwesomeIcon icon={faChevronRight} />
              </div>
            )}
          </button>
        ))}
      </div>

      {/* Footer */}
      <div className="sidebar-footer">
        {!isCollapsed && (
          <div className="sidebar-footer-content">
            <span>Client Dashboard</span>
            <span className="sidebar-footer-version">v2.0</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default SidebarClient;
  