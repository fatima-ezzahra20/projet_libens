import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getReleveDetails } from '../api/relevesApi';
import './ReleveDetails.css';

function ReleveDetails() {
  const { id } = useParams();
  const [releve, setReleve] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        const data = await getReleveDetails(id);
        setReleve(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchDetails();
  }, [id]);

  if (loading) {
    return <div className="loading">Chargement des détails...</div>;
  }

  if (error) {
    return <div className="error">Erreur: {error}</div>;
  }

  if (!releve) {
    return <div className="not-found">Relevé non trouvé.</div>;
  }

  return (
    <div className="releve-details-container">
      <Link to="/releves" className="back-link">Retour à la liste</Link>
      <h1>Détails du relevé</h1>
      
      <div className="details-card">
        <h2>Informations générales</h2>
        <p><strong>Fichier:</strong> {releve.filename}</p>
        <p><strong>Mois du relevé:</strong> {releve.releve_mois}</p>
        <p><strong>Solde final:</strong> {releve.solde ? `${releve.solde.solde} MAD` : 'N/A'}</p>
      </div>

      <div className="transactions-card">
        <h2>Transactions</h2>
        {releve.transactions && releve.transactions.length > 0 ? (
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Libellé</th>
                <th>Montant</th>
              </tr>
            </thead>
            <tbody>
              {releve.transactions.map((transaction, index) => (
                <tr key={index}>
                  <td>{transaction.date}</td>
                  <td>{transaction.libelle}</td>
                  <td>{transaction.montant} MAD</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>Aucune transaction trouvée pour ce relevé.</p>
        )}
      </div>
    </div>
  );
}

export default ReleveDetails;