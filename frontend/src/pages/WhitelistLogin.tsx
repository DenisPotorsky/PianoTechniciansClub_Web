import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../services/api';

const WhitelistLogin: React.FC = () => {
  const [telegram_id, setTelegramId] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const response = await api.post('/auth/whitelist-login', {
        telegram_id: parseInt(telegram_id)
      });

      const { access_token, ...userData } = response.data;
      localStorage.setItem('token', access_token);

      // Обновляем состояние в AuthContext
      navigate('/');
      window.location.reload();

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
          <div className="text-5xl mb-3">👑</div>
          <h2 className="text-3xl font-bold text-white">Вход для избранных</h2>
          <p className="mt-2 text-blue-200 text-sm">
            Вход по Telegram ID (белый список)
          </p>
          <p className="text-blue-300 text-xs mt-1">
            Только для пользователей, добавленных в белый список
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div>
            <label className="block text-sm font-medium text-blue-200">Telegram ID</label>
            <input
              type="number"
              required
              value={telegram_id}
              onChange={(e) => setTelegramId(e.target.value)}
              className="mt-1 w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent"
              placeholder="Введите ваш Telegram ID"
            />
          </div>

          {error && (
            <div className="text-red-400 text-sm text-center bg-red-500/10 border border-red-500/20 p-3 rounded-xl">
              ❌ {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-yellow-500 to-orange-600 hover:from-yellow-600 hover:to-orange-700 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 disabled:opacity-50"
          >
            {loading ? 'Вход...' : '👑 Войти по Telegram ID'}
          </button>

          <div className="text-center space-y-2">
            <Link to="/login" className="text-blue-300 hover:text-blue-200 text-sm transition block">
              🔑 Вход по email
            </Link>
            <Link to="/" className="text-blue-300/50 hover:text-blue-200 text-xs transition block">
              🏠 На главную
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};

export default WhitelistLogin;