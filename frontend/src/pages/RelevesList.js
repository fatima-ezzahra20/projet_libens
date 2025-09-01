import React, { useState, useEffect } from 'react';

import { getReleves } from '../api/relevesApi';

import { Link } from 'react-router-dom';

import ReleveCard from '../components/ReleveCard';

import UploadModal from '../components/UploadModal';

import './RelevesList.css';

import axios from 'axios';



function RelevesList({ searchTerm }) {

const [releves, setReleves] = useState([]); // Garde la liste complète de tous les relevés

const [loading, setLoading] = useState(true);

const [error, setError] = useState(null);

const [isModalOpen, setIsModalOpen] = useState(false);

const [displayedReleves, setDisplayedReleves] = useState([]); // La liste de relevés qui est affichée à l'écran



// Cet effet est responsable de la recherche et de l'affichage




useEffect(() => {

const fetchAndFilterReleves = async () => {

setLoading(true);

setError(null);

try {

if (searchTerm) {

// Si un terme de recherche est présent, on appelle l'API de recherche.

const response = await axios.get(`http://localhost:8000/releves/search?q=${searchTerm}`);

setDisplayedReleves(response.data.releves);

} else {

// Si le terme de recherche est vide, on affiche la liste complète.

const allReleves = await getReleves();

setReleves(allReleves); // Stocke la liste complète

setDisplayedReleves(allReleves); // Et l'affiche

}

} catch (err) {

setError(err.message);

} finally {

setLoading(false);

}

};

fetchAndFilterReleves();

}, [searchTerm]); // Le hook s'exécute à chaque fois que le terme de recherche change



if (loading) {

return <div className="loading">Chargement des relevés en cours...</div>;

}



if (error) {

return <div className="error">Erreur lors du chargement: {error}</div>;

}


const renderContent = () => {

if (displayedReleves.length === 0) {

const message = searchTerm

? "Aucun relevé trouvé pour cette recherche."

: "Aucun relevé trouvé. Téléchargez-en un pour commencer.";


// Ajout d'une classe CSS pour le centrage et le style

return <p className="no-results-message">{message}</p>;

}



return (

<div className="releves-grid">

{displayedReleves.map((releve) => (

<Link to={`/releves/${releve.id}`} key={releve.id} className="releve-link">

<ReleveCard releve={releve} />

</Link>

))}

</div>

);



return (

<div className="releves-grid">

{displayedReleves.map((releve) => (

<Link to={`/releves/${releve.id}`} key={releve.id} className="releve-link">

<ReleveCard releve={releve} />

</Link>

))}

</div>

);

};


return (

<div className="releves-list-container">

<div className="header-with-button">

<h1>Mes Relevés</h1>

<button onClick={() => setIsModalOpen(true)} className="upload-button-list">

+ Upload relevé

</button>

</div>



{renderContent()}



{isModalOpen && <UploadModal onClose={() => setIsModalOpen(false)} />}

</div>

);

}



export default RelevesList;