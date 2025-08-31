// Ajoutez l'importation de la bibliothèque axios
import axios from 'axios';

// L'URL de votre backend reste la même
const API_URL = 'http://127.0.0.1:8000';

// Fonction pour uploader un fichier avec Axios
export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await axios.post(`${API_URL}/upload`, formData, {
      headers: {
        // Axios gère ce type de contenu automatiquement, mais c'est une bonne pratique de le spécifier
        'Content-Type': 'multipart/form-data',
      },
    });
    // Axios retourne les données directement dans la propriété .data
    return response.data;
  } catch (error) {
    // Axios capture automatiquement les erreurs 4xx et 5xx
    console.error("Erreur lors de l'upload:", error);
    throw new Error('Erreur lors du téléchargement du fichier.');
  }
};

// Fonction pour récupérer la liste des relevés avec Axios
export const getReleves = async () => {
  try {
    const response = await axios.get(`${API_URL}/releves`);
    return response.data;
  } catch (error) {
    console.error("Erreur lors de la récupération des relevés:", error);
    throw new Error('Erreur lors de la récupération des relevés.');
  }
};

// Fonction pour récupérer les détails d'un relevé avec Axios
export const getReleveDetails = async (id) => {
  try {
    const response = await axios.get(`${API_URL}/releves/${id}`);
    return response.data;
  } catch (error) {
    console.error("Erreur lors de la récupération des détails:", error);
    throw new Error('Relevé non trouvé.');
  }
};