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
    <div className="max-w-2xl mx-auto py-8">
      <div className="glass-card p-8 max-w-md mx-auto">
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
              className="glass-input w-full mt-1"
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
            className="w-full glass-btn glass-btn-primary py-3 text-lg disabled:opacity-50"
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