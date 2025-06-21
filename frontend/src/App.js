import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage'; // Создадим эту страницу позже
import ProfilePage from './pages/ProfilePage'; // Импортируем страницу профиля
import PropertiesPage from './pages/PropertiesPage'; // Импортируем страницу объектов
import ClientsPage from './pages/ClientsPage'; // Импортируем страницу клиентов
import CalendarPage from './pages/CalendarPage'; // Импортируем страницу календаря
import TrainingPage from './pages/TrainingPage'; // Импортируем страницу обучения
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
            <Route path="profile" element={<ProfilePage />} />
            <Route path="properties" element={<PropertiesPage />} />
            <Route path="clients" element={<ClientsPage />} />
            <Route path="calendar" element={<CalendarPage />} />
            <Route path="training" element={<TrainingPage />} />
            {/* Другие защищенные страницы будут здесь, например: */}
            {/* <Route path="properties" element={<PropertiesPage />} /> */}
          </Route>
        </Route>

      </Routes>
    </Router>
  );
}

export default App; 