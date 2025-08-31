import React from 'react';
import './ReleveCard.css';

function ReleveCard({ releve }) {
  return (
    <div className="releve-card">
      <h3 className="releve-card-title">Relevé de {releve.releve_mois}</h3>
      <div className="releve-card-info">
        <p><strong>Fichier :</strong> {releve.filename}</p>
        <p><strong>Solde :</strong> {releve.solde} MAD</p>
      </div>
      <div className="releve-card-details">
        <span>Voir détails</span>
      </div>
    </div>
  );
}

export default ReleveCard;