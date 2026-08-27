import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import Home from './pages/Home';
import Calculator from './pages/Calculator';
import AgeDetection from './pages/AgeDetection';
import Regulating from './pages/Regulating';
import Strings from './pages/Strings';
import Admin from './pages/Admin';
import Login from './pages/Login';
import RequestAccess from './pages/RequestAccess';
import WhitelistLogin from './pages/WhitelistLogin';
import Profile from './pages/Profile';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* ===== ГЛАВНАЯ ===== */}
          <Route path="/" element={<Layout />}>
            <Route index element={<Home />} />
          </Route>

          {/* ===== ПУБЛИЧНЫЕ СТРАНИЦЫ (С LAYOUT) ===== */}
          <Route path="/login" element={<Layout />}>
            <Route index element={<Login />} />
          </Route>
          <Route path="/request-access" element={<Layout />}>
            <Route index element={<RequestAccess />} />
          </Route>
          <Route path="/whitelist-login" element={<Layout />}>
            <Route index element={<WhitelistLogin />} />
          </Route>
          <Route path="/forgot-password" element={<Layout />}>
            <Route index element={<ForgotPassword />} />
          </Route>
          <Route path="/reset-password" element={<Layout />}>
            <Route index element={<ResetPassword />} />
          </Route>

          {/* ===== ЗАЩИЩЁННЫЕ СТРАНИЦЫ ===== */}
          <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
            <Route path="profile" element={<Profile />} />
            <Route path="calculator" element={<ProtectedRoute requireMember><Calculator /></ProtectedRoute>} />
            <Route path="age" element={<ProtectedRoute requireMember><AgeDetection /></ProtectedRoute>} />
            <Route path="regulating" element={<ProtectedRoute requireMember><Regulating /></ProtectedRoute>} />
            <Route path="strings" element={<ProtectedRoute requireMember><Strings /></ProtectedRoute>} />
            <Route path="admin" element={<ProtectedRoute requireAdmin><Admin /></ProtectedRoute>} />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;