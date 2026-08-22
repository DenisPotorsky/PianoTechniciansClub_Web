import React, { useState } from 'react';
import api from '../services/api';
import { Link } from 'react-router-dom';

const RequestAccess: React.FC = () => {
  const [email, setEmail] = useState('');
  const [full_name, setFullName] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess(false);

    try {
      await api.post('/auth/access-request', {
        email,
        full_name,
        message,
      });
      setSuccess(true);
      setEmail('');
      setFullName('');
      setMessage('');
    } catch (err: any) {
      setError(err.response?.data?.detail || '❌ Ошибка при отправке');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="glass-card p-8">
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">📩</div>
          <h2 className="text-3xl font-bold text-white">Запрос доступа</h2>
          <p className="text-white/50 mt-1">
            Заполните форму, и администратор рассмотрит вашу заявку
          </p>
        </div>

        {success && (
          <div className="glass p-4 rounded-xl mb-6 text-center border-green-500/30 text-green-300">
            ✅ Заявка отправлена! Администратор рассмотрит её в ближайшее время.
          </div>
        )}

        {error && (
          <div className="glass p-4 rounded-xl mb-6 text-center border-red-500/30 text-red-300">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-white/70 mb-1">Email *</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              className="glass-input w-full"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-white/70 mb-1">ФИО *</label>
            <input
              type="text"
              value={full_name}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Иван Иванов"
              className="glass-input w-full"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-white/70 mb-1">Сообщение</label>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Расскажите о себе..."
              className="glass-input w-full min-h-[100px]"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full glass-btn glass-btn-primary py-3 text-lg disabled:opacity-50"
          >
            {loading ? '⏳ Отправка...' : '📩 Отправить заявку'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <Link to="/login" className="text-white/50 hover:text-white transition">
            🔑 Уже есть доступ? Войти
          </Link>
        </div>
      </div>
    </div>
  );
};

export default RequestAccess;