import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка входа');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 py-12 px-4">
      <div className="max-w-md w-full bg-white/10 backdrop-blur-md rounded-3xl shadow-2xl p-8 border border-white/20">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-white">🎹 Вход в клуб</h2>
          <p className="mt-2 text-blue-200 text-sm">
            Введите email и пароль
          </p>
          <p className="text-blue-300 text-xs mt-1">
            Если у вас нет доступа — запросите его ниже
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-blue-200">Email</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent"
                placeholder="Введите ваш email"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-blue-200">Пароль</label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent"
                placeholder="Введите пароль"
              />
            </div>
          </div>

          {error && (
            <div className="text-red-400 text-sm text-center bg-red-500/10 border border-red-500/20 p-3 rounded-xl">
              ❌ {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 disabled:opacity-50"
          >
            {loading ? 'Вход...' : '🔑 Войти'}
          </button>

          <div className="text-center space-y-2">
            <Link to="/request-access" className="text-blue-300 hover:text-blue-200 text-sm transition block">
              Нет доступа? 📩 Запросить доступ
            </Link>
            <Link to="/whitelist-login" className="text-yellow-300 hover:text-yellow-200 text-sm transition block">
              👑 Вход по Telegram ID (для админов)
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Login;