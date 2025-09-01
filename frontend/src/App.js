import React, { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import '@fortawesome/fontawesome-free/css/all.min.css';
import './App.css';
import RelevesList from '../../frontend/src/pages/RelevesList';
import ReleveDetails from '../../frontend/src/pages/ReleveDetails';

import Sidebar from './components/sidebar';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from "./pages/dashboard";


import Factures from './pages/mesfactures';
import FactureDetail from './pages/facture_détails'

import SearchBar from './components/SearchBar';


function App() {
  const [searchTerm, setSearchTerm] = useState('');

  const handleSearch = (term) => {
    setSearchTerm(term);
  };

  return (
    <Router>
      <div className="app-container flex">
        <Sidebar />
        <div className="content p-4 flex-1">
          <Routes>
            <Route path="/factures" element={<Factures  />} />
            <Route path="/facture/:id" element={<FactureDetail />} />

            <Route
              path="/releves"
              element={
                <>
                  <SearchBar onSearch={handleSearch} />
                  <RelevesList searchTerm={searchTerm} />
                </>
              }
            />

            <Route path="/releves/:id" element={<ReleveDetails />} />
             <Route path="/" element={<Dashboard />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;


