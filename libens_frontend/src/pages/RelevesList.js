import React, { useState, useEffect } from 'react';
import { getReleves } from '../api/relevesApi';
import { Link } from 'react-router-dom';
import ReleveCard from '../components/ReleveCard';
import UploadModal from '../components/UploadModal';
import './RelevesList.css';

function RelevesList() {
  const [releves, setReleves] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    const fetchReleves = async () => {
      try {
        const data = await getReleves();
        setReleves(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchReleves();
  }, []);

  if (loading) {
  // You can return a simple message or a styled spinner
  return <div className="loading">Chargement des relevés en cours...</div>;
}

if (error) {
  // Keep the error message to inform the user
  return <div className="error">Erreur lors du chargement: {error}</div>;
}
  return (
    <div className="releves-list-container">
      {/* 1. Ajoutez le bouton d'upload ici */}
      <div className="header-with-button">
        <h1>Mes Relevés</h1>
        <button onClick={() => setIsModalOpen(true)} className="upload-button-list">
          + Upload relevé
        </button>
      </div>

      {releves.length === 0 ? (
        <p>Aucun relevé trouvé. Téléchargez-en un pour commencer.</p>
      ) : (
        <div className="releves-grid">
          {releves.map((releve) => (
            <Link to={`/releves/${releve.id}`} key={releve.id} className="releve-link">
              <ReleveCard releve={releve} />
            </Link>
          ))}
        </div>
      )}

      {/* 2. Placez la modale à l'intérieur de la div principale */}
      {isModalOpen && <UploadModal onClose={() => setIsModalOpen(false)} />}
    </div>
  );
}

export default RelevesList;