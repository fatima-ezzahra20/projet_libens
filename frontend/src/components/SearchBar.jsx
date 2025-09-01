// src/components/SearchBar.jsx
import React from 'react';
import './SearchBar.css';

const SearchBar = ({ onSearch }) => {
  return (
    <div className="search-bar-container">
      <input
        type="text"
        placeholder="Rechercher..."
        // L'événement onChange déclenche la recherche instantanément
        onChange={(e) => onSearch(e.target.value)}
        className="search-input"
      />
      <button 
        onClick={() => onSearch(document.querySelector('.search-input').value)} 
        className="search-button">
        Rechercher
      </button>
    </div>
  );
};

export default SearchBar;