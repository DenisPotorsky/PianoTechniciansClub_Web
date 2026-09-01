import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import api from '../services/api';

// ============ ТИПЫ ============
interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string | null;
  phone: string | null;      // <-- ДОБАВЛЕНО
  city: string | null;       // <-- ДОБАВЛЕНО
  telegram_id: number | null;
  is_subscribed: boolean;
  is_approved: boolean;      // <-- ДОБАВЛЕНО
  is_admin: boolean;
  is_super_admin: boolean;
  is_active: boolean;
  created_at: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  whitelistLogin: (telegramId: number) => Promise<boolean>;
  logout: () => void;
  requestAccess: (data: { full_name: string; email: string; message?: string }) => Promise<boolean>;
}

// ============ КОНТЕКСТ ============
const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // ===== ПРОВЕРКА ТОКЕНА ПРИ ЗАГРУЗКЕ =====
  useEffect(() => {
    const initAuth = async () => {
      const savedToken = localStorage.getItem('token') || localStorage.getItem('access_token');

      console.log('🔍 Проверка токена при загрузке:', savedToken ? 'ЕСТЬ' : 'НЕТ');

      if (savedToken) {
        try {
          setToken(savedToken);
          // Проверяем валидность токена и получаем свежие данные (включая phone/city)
          const response = await api.get('/auth/me', {
            headers: { Authorization: `Bearer ${savedToken}` }
          });
          setUser(response.data);
          console.log('✅ Пользователь авторизован:', response.data.first_name);
        } catch (error) {
          console.error('❌ Ошибка при проверке токена:', error);
          localStorage.removeItem('token');
          localStorage.removeItem('access_token');
          setToken(null);
          setUser(null);
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  // ===== ВХОД ПО EMAIL =====
  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      setLoading(true);
      const response = await api.post('/auth/login', { email, password });

      const { access_token, ...userData } = response.data;

      localStorage.setItem('token', access_token);
      localStorage.setItem('access_token', access_token);

      setToken(access_token);
      setUser(userData);

      console.log('✅ Вход выполнен успешно');
      return true;
    } catch (error: any) {
      console.error('❌ Ошибка входа:', error);
      alert(error.response?.data?.detail || 'Ошибка входа');
      return false;
    } finally {
      setLoading(false);
    }
  };

  // ===== ВХОД ПО TELEGRAM ID =====
  const whitelistLogin = async (telegramId: number): Promise<boolean> => {
    try {
      setLoading(true);
      const response = await api.post('/auth/whitelist-login', { telegram_id: telegramId });

      const { access_token, ...userData } = response.data;

      localStorage.setItem('token', access_token);
      localStorage.setItem('access_token', access_token);

      setToken(access_token);
      setUser(userData);

      console.log('✅ Вход по Telegram ID выполнен успешно');
      return true;
    } catch (error: any) {
      console.error('❌ Ошибка входа по Telegram ID:', error);
      alert(error.response?.data?.detail || 'Ошибка входа');
      return false;
    } finally {
      setLoading(false);
    }
  };

  // ===== ЗАПРОС ДОСТУПА =====
  const requestAccess = async (data: {
    full_name: string;
    email: string;
    message?: string
  }): Promise<boolean> => {
    try {
      setLoading(true);
      await api.post('/auth/request-access', data);
      alert('✅ Заявка отправлена! Ожидайте подтверждения.');
      return true;
    } catch (error: any) {
      console.error('❌ Ошибка отправки заявки:', error);
      alert(error.response?.data?.detail || 'Ошибка отправки заявки');
      return false;
    } finally {
      setLoading(false);
    }
  };

  // ===== ВЫХОД =====
  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('access_token');
    setToken(null);
    setUser(null);
    console.log('👋 Выход выполнен');
  };

  // ===== ПРОВАЙДЕР =====
  return (
    <AuthContext.Provider value={{
      user,
      token,
      loading,
      login,
      whitelistLogin,
      logout,
      requestAccess
    }}>
      {children}
    </AuthContext.Provider>
  );
};

// ===== ХУК ДЛЯ ИСПОЛЬЗОВАНИЯ =====
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;