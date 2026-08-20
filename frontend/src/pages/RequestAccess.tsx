import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api';

const RequestAccess: React.FC = () => {
  const [form, setForm] = useState({
    email: '',
    full_name: '',
    message: '',
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      const response = await api.post('/auth/access-request', form);
      setSuccess(response.data.message);
      setForm({ email: '', full_name: '', message: '' });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка отправки');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 py-12 px-4">
      <div className="max-w-md w-full bg-white/10 backdrop-blur-md rounded-3xl shadow-2xl p-8 border border-white/20">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-white">📩 Запрос доступа</h2>
          <p className="mt-2 text-blue-200 text-sm">
            Заполните форму, и администратор рассмотрит вашу заявку
          </p>
        </div>

        <form className="mt-8 space-y-4" onSubmit={handleSubmit}>
          <div>
            <label className="block text-sm font-medium text-blue-200">Email *</label>
            <input
              type="email"
              required
              value={form.email}
              onChange={(e) => setForm({...form, email: e.target.value})}
              className="mt-1 w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-400"
              placeholder="Введите ваш email"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-blue-200">ФИО *</label>
            <input
              type="text"
              required
              value={form.full_name}
              onChange={(e) => setForm({...form, full_name: e.target.value})}
              className="mt-1 w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-400"
              placeholder="Введите ваше полное имя"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-blue-200">Сообщение</label>
            <textarea
              rows={4}
              value={form.message}
              onChange={(e) => setForm({...form, message: e.target.value})}
              className="mt-1 w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-400"
              placeholder="Расскажите о себе (необязательно)"
            />
          </div>

          {error && (
            <div className="text-red-400 text-sm text-center bg-red-500/10 border border-red-500/20 p-3 rounded-xl">
              ❌ {error}
            </div>
          )}

          {success && (
            <div className="text-green-400 text-sm text-center bg-green-500/10 border border-green-500/20 p-3 rounded-xl">
              ✅ {success}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-green-500 to-teal-600 hover:from-green-600 hover:to-teal-700 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 disabled:opacity-50"
          >
            {loading ? 'Отправка...' : '📨 Отправить запрос'}
          </button>

          <div className="text-center">
            <Link to="/login" className="text-blue-300 hover:text-blue-200 text-sm transition">
              🔑 Уже есть доступ? Войти
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RequestAccess;