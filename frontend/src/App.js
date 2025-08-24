import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import '@fortawesome/fontawesome-free/css/all.min.css';
import './App.css';

import Sidebar from './components/sidebar';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';


import Factures from './pages/mesfactures';
import FactureDetail from './pages/facture_détails'

function App() {
  return (
    <Router>
      <div className="app-container flex">
        <Sidebar />
        <div className="content p-4 flex-1">
          <Routes>
            <Route path="/factures" element={<Factures />} />
              <Route path="/facture/:id" element={<FactureDetail />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;



