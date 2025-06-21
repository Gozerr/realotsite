import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage'; // Создадим эту страницу позже
import MainLayout from './components/MainLayout';
import PrivateRoute from './components/PrivateRoute';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        
        {/* Защищенные роуты */}
        <Route path="/" element={<PrivateRoute />}>
          <Route path="/" element={<MainLayout />}>
            <Route path="dashboard" element={<DashboardPage />} />
            {/* Другие защищенные страницы будут здесь, например: */}
            {/* <Route path="properties" element={<PropertiesPage />} /> */}
          </Route>
        </Route>

      </Routes>
    </Router>
  );
}

export default App; 