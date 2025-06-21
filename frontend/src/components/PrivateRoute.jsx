import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useSelector } from 'react-redux';

const PrivateRoute = () => {
  const { user } = useSelector((state) => state.auth);

  if (!user) {
    // Если пользователя нет, перенаправляем на страницу входа
    return <Navigate to="/login" replace />;
  }

  // Если пользователь есть, показываем вложенный роут (например, дашборд)
  return <Outlet />;
};

export default PrivateRoute; 