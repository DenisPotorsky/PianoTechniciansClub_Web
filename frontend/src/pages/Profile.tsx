import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

const Profile: React.FC = () => {
  const { user, logout } = useAuth();
  const [loading, setLoading] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  const [stats, setStats] = useState<{ count: number; last_date: string | null }>({ count: 0, last_date: null });
  const [form, setForm] = useState({
    first_name: '',
    email: '',
    phone: '',
    city: '',
  });
  const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

  useEffect(() => {
    if (user) {
      setForm({
        first_name: user.first_name || '',
        email: user.email || '',
        phone: user.phone || '',
        city: user.city || '',
      });
    }
    loadStats();
  }, [user]);

  const loadStats = async () => {
    try {
      const response = await api.get('/users/stats');
      setStats(response.data);
    } catch {
      // Не критично
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      await api.put('/users/profile', form);
      setMessage({ text: '✅ Профиль успешно обновлён!', type: 'success' });
    } catch (error: any) {
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

  const handleLogoutFromClub = async () => {
    setLoading(true);
    setShowLogoutConfirm(false);
    try {
      await api.post('/users/logout-club');
      alert('🚪 Вы вышли из клуба.');
      logout();
    } catch (error: any) {
      alert(error.response?.data?.detail || '❌ Ошибка при выходе');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteProfile = async () => {
    setDeleteLoading(true);
    setShowDeleteConfirm(false);
    try {
      await api.delete('/users/profile');
      alert('🗑️ Профиль удалён.');
      logout();
    } catch (error: any) {
      alert(error.response?.data?.detail || '❌ Ошибка при удалении');
    } finally {
      setDeleteLoading(false);
    }
  };

  const createdDate = user?.created_at
    ? new Date(user.created_at).toLocaleDateString('ru-RU')
    : '—';

  const lastCalcDate = stats.last_date
    ? new Date(stats.last_date).toLocaleDateString('ru-RU')
    : '—';

  return (
    <div className="max-w-2xl mx-auto">
      <div className="glass-card p-8">
        <div className="text-center mb-8">
          <div className="text-6xl mb-3">👤</div>
          <h2 className="text-3xl font-bold text-white">Мой профиль</h2>
          <p className="text-white/50 mt-1">Управление личными данными</p>
        </div>

        {message && (
          <div className={`glass p-4 rounded-xl mb-6 text-center ${
            message.type === 'success' ? 'border-green-500/30 text-green-300' : 'border-red-500/30 text-red-300'
          }`}>
            {message.text}
          </div>
        )}

        {/* Статистика */}
        <div className="glass p-4 rounded-xl mb-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-white/50">Статус</p>
              <p className="text-white font-medium">
                {user?.is_super_admin ? '👑 Супер-админ' :
                 user?.is_admin ? '⭐ Админ' : '✅ Участник клуба'}
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-white/50">В клубе с</p>
              <p className="text-white font-medium">{createdDate}</p>
            </div>
          </div>
          <div className="mt-3 pt-3 border-t border-white/5 flex items-center justify-between">
            <div>
              <p className="text-sm text-white/50">Расчётов</p>
              <p className="text-white font-medium">{stats.count}</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-white/50">Последний расчёт</p>
              <p className="text-white font-medium">{lastCalcDate}</p>
            </div>
          </div>
          {user?.telegram_id && (
            <div className="mt-3 pt-3 border-t border-white/5">
              <p className="text-sm text-white/50">Telegram ID</p>
              <p className="text-white font-mono text-sm">{user.telegram_id}</p>
            </div>
          )}
        </div>

        {/* Форма */}
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-white/70 mb-1">Имя</label>
            <input
              type="text"
              name="first_name"
              value={form.first_name}
              onChange={handleChange}
              className="glass-input w-full opacity-60 cursor-not-allowed"
              disabled
              title="Синхронизируется с Telegram"
            />
            <p className="text-xs text-white/30 mt-1">Синхронизируется с Telegram</p>
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

          <div>
            <label className="block text-sm font-medium text-white/70 mb-1">Телефон</label>
            <input
              type="tel"
              name="phone"
              value={form.phone}
              onChange={handleChange}
              className="glass-input w-full"
              placeholder="+7 (999) 123-45-67"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-white/70 mb-1">Город</label>
            <input
              type="text"
              name="city"
              value={form.city}
              onChange={handleChange}
              className="glass-input w-full"
              placeholder="Москва"
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

        {/* Опасные действия */}
        <div className="mt-8 pt-6 border-t border-white/10 space-y-3">
          <button
            onClick={() => setShowLogoutConfirm(true)}
            disabled={loading}
            className="w-full glass-btn py-3 text-lg disabled:opacity-50"
            style={{ background: 'rgba(251, 191, 36, 0.15)', borderColor: 'rgba(251, 191, 36, 0.3)', color: '#fbbf24' }}
          >
            🚪 Выйти из клуба
          </button>

          <button
            onClick={() => setShowDeleteConfirm(true)}
            disabled={deleteLoading}
            className="w-full glass-btn py-3 text-lg disabled:opacity-50"
            style={{ background: 'rgba(239, 68, 68, 0.15)', borderColor: 'rgba(239, 68, 68, 0.3)', color: '#f87171' }}
          >
            🗑️ Удалить профиль
          </button>
        </div>
      </div>

      {/* Модалка выхода */}
      {showLogoutConfirm && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="glass-card p-8 max-w-md w-full">
            <h3 className="text-xl font-bold text-white mb-4">⚠️ Выйти из клуба?</h3>
            <p className="text-white/70 mb-6">
              При выходе:<br/>
              • Все расчёты будут удалены<br/>
              • Доступ к инструментам закрыт<br/>
              • Можно подать заявку снова
            </p>
            <div className="flex gap-3">
              <button onClick={() => setShowLogoutConfirm(false)} className="flex-1 glass-btn py-3">❌ Отмена</button>
              <button onClick={handleLogoutFromClub} className="flex-1 glass-btn py-3"
                style={{ background: 'rgba(251, 191, 36, 0.2)', borderColor: 'rgba(251, 191, 36, 0.3)', color: '#fbbf24' }}>
                🚪 Да, выйти
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Модалка удаления */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="glass-card p-8 max-w-md w-full">
            <h3 className="text-xl font-bold text-white mb-4">🗑️ Удалить профиль?</h3>
            <p className="text-white/70 mb-6">
              Это действие <strong>необратимо</strong>!<br/><br/>
              Будут удалены все данные, расчёты и история.
            </p>
            <div className="flex gap-3">
              <button onClick={() => setShowDeleteConfirm(false)} className="flex-1 glass-btn py-3">❌ Отмена</button>
              <button onClick={handleDeleteProfile} className="flex-1 glass-btn py-3"
                style={{ background: 'rgba(239, 68, 68, 0.2)', borderColor: 'rgba(239, 68, 68, 0.3)', color: '#f87171' }}>
                ⚠️ Да, удалить
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Profile;