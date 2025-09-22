import React, { useState } from 'react';
import './SidebarClient.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faHistory, 
  faUser, 
  faBars, 
  faTimes,
  faChevronRight,
  faLeaf
} from '@fortawesome/free-solid-svg-icons';

const SidebarClient = ({ activeSection, onSectionChange }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isVisible, setIsVisible] = useState(true);

  const toggleSidebar = () => {
    setIsCollapsed(!isCollapsed);
  };

  const toggleVisibility = () => {
    setIsVisible(!isVisible);
  };

  const menuItems = [
    {
      id: 'historique',
      label: 'Historique',
      icon: faHistory,
      description: ' '
    },
    {
      id: 'profile',
      label: 'Profil',
      icon: faUser,
      description: 'Gérer votre profil'
    }
  ];

  const handleItemClick = (itemId) => {
    if (onSectionChange) {
      onSectionChange(itemId);
    }
  };

  if (!isVisible) {
    return (
      <div className="sidebar-toggle-button" onClick={toggleVisibility}>
        <FontAwesomeIcon icon={faBars} />
      </div>
    );
  }

  return (
    <div className={`sidebar-client ${isCollapsed ? 'collapsed' : ''}`}>
      {/* En-tête du sidebar */}
      <div className="sidebar-header">
        <div className="sidebar-brand">
          <FontAwesomeIcon icon={faLeaf} className="sidebar-brand-icon" />
          {!isCollapsed && <span className="sidebar-brand-text">AgriPredict</span>}
        </div>  
        <div className="sidebar-controls">
          <button 
            className="sidebar-collapse-btn" 
            onClick={toggleSidebar}
            title={isCollapsed ? "Développer" : "Réduire"}
          >
            <FontAwesomeIcon icon={isCollapsed ? faChevronRight : faTimes} />
          </button>
        </div>
      </div>

      {/* Menu principal */}
      <div className="sidebar-menu">
        <div className="sidebar-menu-section">
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
      </div>

      {/* Footer du sidebar */}
      <div className="sidebar-footer">
        {!isCollapsed && (
          <div className="sidebar-footer-content">
            <div className="sidebar-footer-text">
              <span>Client Dashboard</span>
              <span className="sidebar-footer-version">v2.0</span>
            </div>  
          </div>  
        )}
      </div>
    </div>
  );
};

export default SidebarClient; 