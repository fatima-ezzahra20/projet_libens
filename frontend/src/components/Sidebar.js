import React from 'react';
import { Link } from 'react-router-dom';
import './Sidebar.css';

function Sidebar() {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h1>Libens consulting</h1>
      </div>
      <nav className="sidebar-nav">
        
        <Link to="/releves" className="nav-item">
          <span className="icon">📊</span> Mes Relevés
        </Link>
      </nav>
    </div>
  );
}

export default Sidebar;