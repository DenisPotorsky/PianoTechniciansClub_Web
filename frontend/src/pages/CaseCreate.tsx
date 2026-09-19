import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const CaseCreate: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    title: '',
    symptom: '',
    diagnosis: '',
    solution: '',
    tools_used: '',
    difficulty: 'medium',
    tags: '' as string,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const tagsArray = form.tags.split(',').map(t => ({ tag: t.trim() })).filter(t => t.tag);
      await api.post('/cases/', {
        ...form,
        tags: tagsArray,
        media: [],
      });
      navigate('/cases');
    } catch (err) {
      alert('Ошибка создания кейса');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold text-white mb-8">➕ Новый кейс</h1>
      
      <form onSubmit={handleSubmit} className="glass-card rounded-2xl p-8 space-y-6">
        <div>
          <label className="block text-white/80 mb-2">Заголовок *</label>
          <input
            type="text"
            value={form.title}
            onChange={e => setForm({...form, title: e.target.value})}
            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white"
            required
            minLength={3}
          />
        </div>

        <div>
          <label className="block text-white/80 mb-2">Симптом проблемы *</label>
          <textarea
            value={form.symptom}
            onChange={e => setForm({...form, symptom: e.target.value})}
            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white h-24"
            required
            minLength={10}
            placeholder="Например: глухой звук в теноре после замены струны"
          />
        </div>

        <div>
          <label className="block text-white/80 mb-2">Диагностика</label>
          <textarea
            value={form.diagnosis}
            onChange={e => setForm({...form, diagnosis: e.target.value})}
            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white h-24"
            placeholder="Как выявили причину проблемы"
          />
        </div>

        <div>
          <label className="block text-white/80 mb-2">Решение *</label>
          <textarea
            value={form.solution}
            onChange={e => setForm({...form, solution: e.target.value})}
            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white h-32"
            required
            minLength={10}
            placeholder="Пошаговое описание решения"
          />
        </div>

        <div>
          <label className="block text-white/80 mb-2">Использованные инструменты</label>
          <input
            type="text"
            value={form.tools_used}
            onChange={e => setForm({...form, tools_used: e.target.value})}
            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white"
            placeholder="Например: камертон, клинья, войлок"
          />
        </div>

        <div>
          <label className="block text-white/80 mb-2">Сложность</label>
          <select
            value={form.difficulty}
            onChange={e => setForm({...form, difficulty: e.target.value})}
            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white"
          >
            <option value="easy">🟢 Легко</option>
            <option value="medium">🟡 Средне</option>
            <option value="hard">🔴 Сложно</option>
          </select>
        </div>

        <div>
          <label className="block text-white/80 mb-2">Теги (через запятую)</label>
          <input
            type="text"
            value={form.tags}
            onChange={e => setForm({...form, tags: e.target.value})}
            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white"
            placeholder="steinway, тенор, струны, настройка"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full glass-btn glass-btn-primary py-4 rounded-xl text-lg font-semibold disabled:opacity-50"
        >
          {loading ? 'Создание...' : '✅ Опубликовать кейс'}
        </button>
      </form>
    </div>
  );
};

export default CaseCreate;
