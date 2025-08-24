import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { ArrowLeft } from 'lucide-react';
import './facture_détails.css';

function FactureDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [facture, setFacture] = useState(null);
  const [lignes, setLignes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios
      .get(`http://127.0.0.1:8000/facture/${id}`)
      .then((res) => {
        setFacture(res.data.facture);
        setLignes(res.data.lignes);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, [id]);

  if (loading) return <p>Chargement de la facture...</p>;
  if (!facture) return <p>Facture introuvable.</p>;

  return (
    <div className="facture-container">
      {/* Header */}
      <div className="facture-header-row">
        <span className="back-arrow" onClick={() => navigate(-1)}>
          <ArrowLeft size={20} />
        </span>
        <div>
          <h2>Détails de la facture {facture.num_facture}</h2>
          <p className="text-muted">Date : {facture.date_emission}</p>
        </div>
      </div>

      {/* Informations générales */}
      <div className="card">
        <h3>Informations générales</h3>
        <div className="facture-details-grid">
          <p><strong>Fournisseur :</strong> {facture.fournisseur}</p>
          <p><strong>Date émission :</strong> {facture.date_emission}</p>
          <p><strong>Montant TTC :</strong> {facture.montant_total_ttc} MAD</p>
          <p><strong>Rib :</strong> {facture.rib_iban}</p>
          <p><strong>Date échéance :</strong> {facture.date_echeance}</p>
          <p><strong>Montant HT :</strong> {facture.montant_total_ht} MAD</p>
        </div>
      </div>

      {/* Produits */}
      <div className="card">
        <h3>Produits</h3>
        <table className="table">
          <thead>
            <tr>
              <th>Produit</th>
              <th>Quantité</th>
              <th>Prix Unitaire</th>
              <th>Total</th>
            </tr>
          </thead>
          <tbody>
            {lignes.map((ligne) => (
              <tr key={ligne.id}>
                <td>{ligne.description_ligne}</td>
                <td>{ligne.quantite}</td>
                <td>{ligne.prix_unitaire_ht} MAD</td>
                <td>{ligne.montant_ligne} MAD</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default FactureDetail;
