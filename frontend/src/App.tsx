import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import Home from './pages/Home';
import Calculator from './pages/Calculator';
import AgeDetection from './pages/AgeDetection';
import Regulating from './pages/Regulating';  // 👈 НОВАЯ СТРАНИЦА
import Admin from './pages/Admin';
import Login from './pages/Login';
import RequestAccess from './pages/RequestAccess';
import WhitelistLogin from './pages/WhitelistLogin';
import Profile from './pages/Profile';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Публичные страницы (без авторизации) */}
          <Route path="/login" element={<Login />} />
          <Route path="/request-access" element={<RequestAccess />} />
          <Route path="/whitelist-login" element={<WhitelistLogin />} />

          {/* Защищённые страницы (с авторизацией) */}
          <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
            <Route index element={<Home />} />
            <Route path="profile" element={<Profile />} />

            {/* Доступно только для подписанных участников */}
            <Route path="calculator" element={
              <ProtectedRoute requireMember>
                <Calculator />
              </ProtectedRoute>
            } />

            <Route path="age" element={
              <ProtectedRoute requireMember>
                <AgeDetection />
              </ProtectedRoute>
            } />

            {/* 👇 НОВЫЙ МАРШРУТ - РЕГУЛИРОВКА */}
            <Route path="regulating" element={
              <ProtectedRoute requireMember>
                <Regulating />
              </ProtectedRoute>
            } />

            {/* Доступно только для админов */}
            <Route path="admin" element={
              <ProtectedRoute requireAdmin>
                <Admin />
              </ProtectedRoute>
            } />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;