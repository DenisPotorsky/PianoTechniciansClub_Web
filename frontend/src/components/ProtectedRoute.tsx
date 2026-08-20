import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAuth?: boolean;
  requireMember?: boolean;
  requireAdmin?: boolean;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requireAuth = true,
  requireMember = false,
  requireAdmin = false,
}) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="flex justify-center items-center h-screen text-lg">Загрузка...</div>;
  }

  if (requireAuth && !user) {
    return <Navigate to="/login" replace />;
  }

  if (requireMember && !user?.is_subscribed) {
    return <Navigate to="/profile" replace />;
  }

  if (requireAdmin && !user?.is_admin && !user?.is_super_admin) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;