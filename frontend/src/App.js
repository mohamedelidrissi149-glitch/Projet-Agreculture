import React from 'react'; 
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Prediction from './pages/Prediction';
import AdminClients from './pages/AdminClients';
import HistoriquePredictionsTotal from './pages/HistoriquePredictionsTotal'; // Ajout de l'import  
import CreationAccountAgriculteur from './pages/CreationAccountAgriculteur';
  
   
            
function App() { 
  return (   
    <Router>       
      <Routes>
        <Route path="/" element={<Login />} />   
        <Route path="/login" element={<Login />} /> 
        <Route path="/register" element={<Register />} />
        <Route path="/Prediction" element={<Prediction />} /> 
        <Route path="/AdminClients" element={<AdminClients />} />
        <Route path="/Historique" element={<HistoriquePredictionsTotal />} /> {/* Nouvelle route */}   
        <Route path="/GestionAgriculteurs" element={<AdminClients />} />   
        <Route path="/Prediction" element={<Prediction />} /> 
        <Route path="/admin/create-agriculteur" element={<CreationAccountAgriculteur />} />      
      </Routes>          
    </Router>   
  );    
}  
      
export default App;   