import React, { useState } from 'react';
import { uploadFile } from '../api/relevesApi';
import './UploadModal.css';

function UploadModal({ onClose }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setMessage('Veuillez sélectionner un fichier.');
      return;
    }

    setLoading(true);
    setMessage('Traitement en cours...');

    try {
      await uploadFile(selectedFile);
      setMessage(`Fichier traité avec succès !`);
      // Ferme la modale après un court délai pour que l'utilisateur voie le message
      setTimeout(() => {
        onClose(); 
        window.location.reload(); // Rafraîchit la page pour afficher le nouveau relevé
      }, 1500);
    } catch (error) {
      setMessage(`Erreur : ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <button className="modal-close-button" onClick={onClose}>&times;</button>
        <h2>Télécharger un relevé</h2>
        <p>Sélectionnez un fichier PDF pour l'analyse.</p>
        <label htmlFor="file-upload" className="custom-file-upload">
    <input id="file-upload" type="file" onChange={handleFileChange} />
    <span className="upload-icon">📁</span>
    {selectedFile ? selectedFile.name : "Cliquez pour télécharger un fichier"}
</label>
        <button onClick={handleUpload} disabled={loading} className="upload-button">
          {loading ? 'Chargement...' : 'Télécharger'}
        </button>
        {message && <p className="message">{message}</p>}
      </div>
    </div>
  );
}

export default UploadModal;