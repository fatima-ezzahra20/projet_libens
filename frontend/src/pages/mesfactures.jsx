import React, { useEffect, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import { FaEye } from "react-icons/fa";
import "./mesfactures.css";

function MesFactures() {
  const [factures, setFactures] = useState([]);
  const [filteredFactures, setFilteredFactures] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const userId = 1; // ⚠️ remplacer par l’ID de l’utilisateur connecté

  // Chargement des factures
  useEffect(() => {
    axios
      .get(`http://127.0.0.1:8000/factures/${userId}`)
      .then((res) => {
        setFactures(res.data);
        setFilteredFactures(res.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Erreur lors du chargement :", err);
        setLoading(false);
      });
  }, []);

  // Filtrage en fonction de la recherche
  useEffect(() => {
    const filtered = factures.filter(
      (f) =>
        f.num_facture.toLowerCase().includes(searchTerm.toLowerCase()) ||
        f.fournisseur.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredFactures(filtered);
  }, [searchTerm, factures]);

  // Upload d'une facture
  const handleUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("facture", file);

    axios
      .post("http://127.0.0.1:8000/factures/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then((res) => {
        alert("Facture uploadée et traitée !");
        setFactures((prev) => [...prev, res.data]);
      })
      .catch((err) => {
        console.error(err);
        alert("Erreur lors de l'upload de la facture.");
      });
  };

  if (loading) return <p>Chargement des factures...</p>;

  return (
    <div className="factures-container">
      {/* Header avec recherche et upload */}
<div className="factures-header">
  <h2 className="header-title">Mes Factures</h2>

  <div className="header-actions">
    <input
      type="text"
      placeholder="Rechercher une facture..."
      value={searchTerm}
      onChange={(e) => setSearchTerm(e.target.value)}
      className="search-input"
    />

    <button
      className="search-button"
      onClick={() => console.log("Recherche :", searchTerm)}
    >
      Rechercher
    </button>

    <input
      type="file"
      id="upload-facture"
      accept=".pdf,.png,.jpg,.jpeg"
      style={{ display: "none" }}
      onChange={handleUpload}
    />
    <button
      className="btn-add"
      onClick={() =>
        document.getElementById("upload-facture").click()
      }
    >
      + Upload facture
    </button>
  </div>
</div>


      {/* Liste des factures */}
      {filteredFactures.length === 0 ? (
        <p>Aucune facture trouvée.</p>
      ) : (
        <div className="factures-grid">
          {filteredFactures.map((facture) => (
            <div key={facture.id} className="facture-card">
              <div className="facture-header">
                <h3>{facture.num_facture}</h3>
              </div>

              <div className="facture-info">
                <p>
                  Montant TTC : <strong>{facture.montant_total_ttc} MAD</strong>
                </p>
                <p>
                  Fournisseur : <strong>{facture.fournisseur}</strong>
                </p>
                <p>
                  Date émission : <strong>{facture.date_emission}</strong>
                </p>
                <p>
                  Date échéance : <strong>{facture.date_echeance}</strong>
                </p>
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
