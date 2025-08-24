import React from 'react';
import { Link } from "react-router-dom";
import './sidebar.css';
import { FaFileInvoice } from 'react-icons/fa'; // Pour ajouter une icône

function Sidebar() {
  return (
    <div className="sidebar">
      <h2 className="sidebar-title">Libens consulting</h2>
      <ul className="sidebar-list">
        <li className="sidebar-item">
          <Link to="/factures" className="sidebar-link">
            <FaFileInvoice className="sidebar-icon" /> Factures
          </Link>
        </li>
        <li>
           <FaFileInvoice className="sidebar-icon" /> Relevés
        </li>
      </ul>
    </div>
  );
}

export default Sidebar;
