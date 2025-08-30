import React, { useState } from 'react';
import { uploadFile } from '../api/relevesApi';
import './UploadPage.css';

function UploadPage() {
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
      const result = await uploadFile(selectedFile);
      setMessage(`Fichier "${result.filename}" traité avec succès !`);
      setSelectedFile(null);
    } catch (error) {
      setMessage(`Erreur : ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-container">
      <div className="upload-box">
        <h1>Télécharger un relevé</h1>
        <p>Veuillez télécharger un fichier PDF pour l'analyse.</p>
        <input type="file" onChange={handleFileChange} className="file-input" />
        <button onClick={handleUpload} disabled={loading} className="upload-button">
          {loading ? 'Chargement...' : 'Télécharger'}
        </button>
        {message && <p className="message">{message}</p>}
      </div>
    </div>
  );
}

export default UploadPage;