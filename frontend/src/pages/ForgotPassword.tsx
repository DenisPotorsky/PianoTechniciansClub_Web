import React, { useState } from 'react';
import api from '../services/api';
import { Link } from 'react-router-dom';

const ForgotPassword: React.FC = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess(false);

    try {
      await api.post('/auth/request-password-reset', null, {
        params: { email }
      });
      setSuccess(true);
    } catch (err: any) {
      console.error('Ошибка:', err);
      const errorMessage = err.response?.data?.detail || err.message || '❌ Ошибка при отправке';
      setError(typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto mt-20">
      <div className="glass-card p-8">
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">🔑</div>
          <h2 className="text-3xl font-bold text-white">Восстановление пароля</h2>
          <p className="text-white/50 mt-1">
            Введите email, и мы отправим ссылку для сброса пароля
          </p>
        </div>

        {success && (
          <div className="glass p-4 rounded-xl mb-6 text-center border-green-500/30 text-green-300">
            ✅ Ссылка для сброса отправлена на вашу почту
          </div>
        )}

        {error && (
          <div className="glass p-4 rounded-xl mb-6 text-center border-red-500/30 text-red-300">
            ❌ {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-white/70 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              className="glass-input w-full"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full glass-btn glass-btn-primary py-3 text-lg disabled:opacity-50"
          >
            {loading ? '⏳ Отправка...' : '📩 Отправить ссылку'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <Link to="/login" className="text-white/50 hover:text-white transition">
            ← Вернуться к входу
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;