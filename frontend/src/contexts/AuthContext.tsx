import React, { createContext, useState, useContext, useEffect } from 'react';
import api from '../services/api';

interface User {
  id: number;
  telegram_id: number;
  email: string | null;
  username: string;
  first_name: string;
  last_name: string | null;
  is_subscribed: boolean;
  is_admin: boolean;
  is_super_admin: boolean;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  whitelistLogin: (telegram_id: number) => Promise<void>;
  logout: () => void;
  requestAccess: (message?: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    if (savedToken) {
      setToken(savedToken);
      fetchUser(savedToken);
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUser = async (t: string) => {
    try {
      const response = await api.get('/auth/me', {
        headers: { Authorization: `Bearer ${t}` }
      });
      setUser(response.data);
    } catch (error) {
      localStorage.removeItem('token');
      setToken(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    const { access_token, ...userData } = response.data;
    localStorage.setItem('token', access_token);
    setToken(access_token);
    setUser(userData);
  };

  const whitelistLogin = async (telegram_id: number) => {
    const response = await api.post('/auth/whitelist-login', { telegram_id });
    const { access_token, ...userData } = response.data;
    localStorage.setItem('token', access_token);
    setToken(access_token);
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  const requestAccess = async (message?: string) => {
    await api.post('/auth/access-request', { message });
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, whitelistLogin, logout, requestAccess }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};

export default AuthContext;