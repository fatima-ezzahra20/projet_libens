import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import UploadPage from './pages/UploadPage';
import RelevesList from './pages/RelevesList';
import ReleveDetails from './pages/ReleveDetails';
import Sidebar from './components/Sidebar';
import './App.css'; 

function App() {
  return (
    <Router>
      <div className="app-container">
        <Sidebar />
        <div className="main-content">
          <Routes>
            <Route path="/" element={<UploadPage />} />
            <Route path="/releves" element={<RelevesList />} />
            <Route path="/releves/:id" element={<ReleveDetails />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;