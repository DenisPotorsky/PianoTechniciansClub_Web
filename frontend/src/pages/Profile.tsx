import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

const Profile: React.FC = () => {
  const { user, logout, requestAccess } = useAuth();
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');

  const handleRequestAccess = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setSuccess('');
    try {
      await requestAccess(message);
      setSuccess('✅ Заявка отправлена! Ожидайте подтверждения администратора.');
      setMessage('');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка');
    } finally {
      setLoading(false);
    }
  };

  if (!user) return null;

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-2xl shadow-2xl p-8">
        <h2 className="text-3xl font-bold text-center text-blue-800 mb-6">👤 Профиль</h2>

        <div className="space-y-4">
          <div className="flex justify-between border-b pb-2">
            <span className="font-medium text-gray-600">Имя пользователя</span>
            <span className="text-gray-900">{user.username}</span>
          </div>
          <div className="flex justify-between border-b pb-2">
            <span className="font-medium text-gray-600">Имя</span>
            <span className="text-gray-900">{user.first_name} {user.last_name || ''}</span>
          </div>
          <div className="flex justify-between border-b pb-2">
            <span className="font-medium text-gray-600">Telegram ID</span>
            <span className="text-gray-900">{user.telegram_id}</span>
          </div>
          <div className="flex justify-between border-b pb-2">
            <span className="font-medium text-gray-600">Статус</span>
            <span>
              {user.is_subscribed ? (
                <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">✅ Участник</span>
              ) : (
                <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm">⏳ Ожидает доступа</span>
              )}
            </span>
          </div>
          <div className="flex justify-between border-b pb-2">
            <span className="font-medium text-gray-600">Роль</span>
            <span>
              {user.is_super_admin ? '👑 Супер-админ' : user.is_admin ? '⭐ Админ' : '👤 Пользователь'}
            </span>
          </div>
        </div>

        {!user.is_subscribed && (
          <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-xl">
            <h3 className="font-semibold text-yellow-800 mb-2">📩 Запросить доступ</h3>
            <p className="text-sm text-yellow-700 mb-3">
              Чтобы получить доступ к калькулятору и другим функциям, отправьте заявку администратору.
            </p>
            <form onSubmit={handleRequestAccess}>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Напишите сообщение администратору (необязательно)"
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 mb-3"
                rows={3}
              />
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Отправка...' : '📩 Отправить заявку'}
              </button>
            </form>
            {success && <p className="mt-3 text-green-700">{success}</p>}
          </div>
        )}

        <button
          onClick={logout}
          className="mt-6 w-full py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
        >
          🚪 Выйти
        </button>
      </div>
    </div>
  );
};

export default Profile;