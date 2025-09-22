import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Prediction from './pages/Prediction';
import AdminClients from './pages/AdminClients';
    

function App() {
  return (
    <Router>  
      <Routes>
        <Route path="/" element={<Login />} /> 
        <Route path="/login" element={<Login />} /> 
        <Route path="/register" element={<Register />} />
        <Route path="/Prediction" element={<Prediction />} /> 
        <Route path="/AdminClients" element={<AdminClients />} />
      </Routes> 
    </Router> 
  );
}  
   
export default App;
  