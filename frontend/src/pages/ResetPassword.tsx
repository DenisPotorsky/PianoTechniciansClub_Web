import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Link, useNavigate, useLocation } from 'react-router-dom';

const ResetPassword: React.FC = () => {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [token, setToken] = useState('');
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const tokenParam = params.get('token');
    if (tokenParam) {
      setToken(tokenParam);
    } else {
      setError('❌ Неверная ссылка для сброса пароля');
    }
  }, [location]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      setError('❌ Пароли не совпадают');
      return;
    }

    if (password.length < 6) {
      setError('❌ Пароль должен содержать минимум 6 символов');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess(false);

    try {
      await api.post('/auth/reset-password', null, {
        params: { token, new_password: password }
      });
      setSuccess(true);
      setTimeout(() => navigate('/login'), 3000);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || '❌ Ошибка при сбросе пароля';
      setError(typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto mt-20">
      <div className="glass-card p-8">
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">🔐</div>
          <h2 className="text-3xl font-bold text-white">Создание нового пароля</h2>
          <p className="text-white/50 mt-1">Введите новый пароль для вашего аккаунта</p>
        </div>

        {success && (
          <div className="glass p-4 rounded-xl mb-6 text-center border-green-500/30 text-green-300">
            ✅ Пароль успешно изменён! Перенаправление на вход...
          </div>
        )}

        {error && (
          <div className="glass p-4 rounded-xl mb-6 text-center border-red-500/30 text-red-300">
            ❌ {error}
          </div>
        )}

        {token && !success && (
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-white/70 mb-1">Новый пароль</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Минимум 6 символов"
                className="glass-input w-full"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-white/70 mb-1">Подтверждение пароля</label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Повторите пароль"
                className="glass-input w-full"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full glass-btn glass-btn-primary py-3 text-lg disabled:opacity-50"
            >
              {loading ? '⏳ Сохранение...' : '💾 Сохранить пароль'}
            </button>
          </form>
        )}

        <div className="mt-6 text-center">
          <Link to="/login" className="text-white/50 hover:text-white transition">
            ← Вернуться к входу
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ResetPassword;