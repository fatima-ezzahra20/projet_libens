import React, { useEffect, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import "./mesfactures.css"; // Nouveau fichier CSS pour les cartes
import { FaEye } from "react-icons/fa";

function MesFactures() {
  const [factures, setFactures] = useState([]);
  const [loading, setLoading] = useState(true);
  const userId = 1; // ⚠️ à remplacer par l’ID de l’utilisateur connecté

  useEffect(() => {
    axios
      .get(`http://127.0.0.1:8000/factures/${userId}`)
      .then((res) => {
        setFactures(res.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Erreur lors du chargement :", err);
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Chargement des factures...</p>;
  const handleUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("facture", file);

    axios.post("http://127.0.0.1:8000/factures/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    })
    .then((res) => {
      alert("Facture uploadée et traitée !");
      setFactures(prev => [...prev, res.data]); // Ajoute la nouvelle facture à la liste
    })
    .catch((err) => {
      console.error(err);
      alert("Erreur lors de l'upload de la facture.");
    });
  };

  return (
    <div className="factures-container">
      <div className="factures-header">
  <h2>Mes Factures</h2>
  
  <div>
    <input
      type="file"
      id="upload-facture"
      accept=".pdf,.png,.jpg,.jpeg"
      style={{ display: "none" }}
      onChange={(e) => handleUpload(e)}
      
    />
    <button
      className="btn-add"
      onClick={() => document.getElementById("upload-facture").click()}
    >
      + Upload facture
    </button>
  </div>
</div>

      {factures.length === 0 ? (
        <p>Aucune facture trouvée.</p>
      ) : (
        <div className="factures-grid">
          {factures.map((facture) => (
            <div key={facture.id} className="facture-card">
              <div className="facture-header">
                <h3>{facture.num_facture}</h3>
                
              </div>

             <div className="facture-info">
                <p>
                  Montant TTC : <strong>{facture.montant_total_ttc} MAD</strong>
                </p>
                <p>Fournisseur : <strong>{facture.fournisseur}</strong></p>
                <p>Date émission : <strong>{facture.date_emission}</strong></p>
                <p>Date échéance : <strong>{facture.date_echeance}</strong></p>
                
              </div>

              <div className="facture-footer">
                <Link to={`/facture/${facture.id}`}>
                  <button className="btn-details">
                    <FaEye style={{ marginRight: "5px" }} /> Voir détails
                  </button>
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default MesFactures;
