import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

const Profile: React.FC = () => {
  const { user, logout } = useAuth();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    username: '',
    email: '',
  });
  const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

  useEffect(() => {
    if (user) {
      setForm({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        username: user.username || '',
        email: user.email || '',
      });
    }
  }, [user]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      // Отправляем данные на сервер
      const response = await api.put('/users/profile', form);

      setMessage({ text: '✅ Профиль успешно обновлён!', type: 'success' });

      // Обновляем данные пользователя в контексте
      const meResponse = await api.get('/auth/me');
      // Здесь нужно обновить контекст (если есть функция updateUser)

    } catch (error: any) {
      console.error('Ошибка:', error);
      setMessage({
        text: error.response?.data?.detail || '❌ Ошибка при обновлении профиля',
        type: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="glass-card p-8">
        <div className="text-center mb-8">
          <div className="text-6xl mb-3">👤</div>
          <h2 className="text-3xl font-bold text-white">Профиль</h2>
          <p className="text-white/50 mt-1">Управление личными данными</p>
        </div>

        {message && (
          <div className={`glass p-4 rounded-xl mb-6 text-center ${
            message.type === 'success' ? 'border-green-500/30 text-green-300' : 'border-red-500/30 text-red-300'
          }`}>
            {message.text}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-white/70 mb-1">Имя</label>
            <input
              type="text"
              name="first_name"
              value={form.first_name}
              onChange={handleChange}
              className="glass-input w-full"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-white/70 mb-1">Фамилия</label>
            <input
              type="text"
              name="last_name"
              value={form.last_name}
              onChange={handleChange}
              className="glass-input w-full"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-white/70 mb-1">Имя пользователя</label>
            <input
              type="text"
              name="username"
              value={form.username}
              onChange={handleChange}
              className="glass-input w-full"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-white/70 mb-1">Email</label>
            <input
              type="email"
              name="email"
              value={form.email}
              onChange={handleChange}
              className="glass-input w-full"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full glass-btn glass-btn-primary py-3 text-lg disabled:opacity-50"
          >
            {loading ? '⏳ Сохранение...' : '💾 Сохранить изменения'}
          </button>
        </form>

        <div className="mt-6 pt-6 border-t border-white/10">
          <div className="glass p-4 rounded-xl">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-white/50">Статус</p>
                <p className="text-white font-medium">
                  {user?.is_subscribed ? '✅ Подписан' : '⏳ Ожидает подписки'}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm text-white/50">Роль</p>
                <p className="text-white font-medium">
                  {user?.is_super_admin ? '👑 Супер-админ' :
                   user?.is_admin ? '⭐ Админ' : '👤 Пользователь'}
                </p>
              </div>
            </div>
            {user?.telegram_id && (
              <div className="mt-2 pt-2 border-t border-white/5">
                <p className="text-sm text-white/50">Telegram ID</p>
                <p className="text-white font-mono text-sm">{user.telegram_id}</p>
              </div>
            )}
          </div>
        </div>

        <button
          onClick={logout}
          className="mt-6 w-full glass-btn py-3 text-lg"
          style={{ background: 'rgba(239, 68, 68, 0.2)', borderColor: 'rgba(239, 68, 68, 0.3)', color: '#f87171' }}
        >
          🚪 Выйти из аккаунта
        </button>
      </div>
    </div>
  );
};

export default Profile;