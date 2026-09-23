import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';


const CaseEdit: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    title: '',
    symptom_text: '',
    diagnosis: '',
    solution_text: '',
    tools_used: '',
    difficulty: 'medium',
  });
  const [changeSummary, setChangeSummary] = useState('');

  useEffect(() => {
    if (id) loadCase();
  }, [id]);


  const loadCase = async () => {
    try {
      const res = await api.get(`/cases/${id}`);
      const c = res.data;
      setForm({
        title: c.title || '',
        symptom_text: c.symptom_text || '',
        diagnosis: c.diagnosis || '',
        solution_text: c.solutions?.[0]?.text || '',
        tools_used: c.tools_used || '',
        difficulty: c.difficulty || 'medium',
      });
    } catch (err) { console.error('Failed to load case'); }
  };



  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.put(`/cases/${id}`, {
        title: form.title,
        symptom_text: form.symptom_text,
        diagnosis: form.diagnosis,
        tools_used: form.tools_used,
        difficulty: form.difficulty,
        change_summary: changeSummary || 'Обновление кейса',
      });
      navigate(`/cases/${id}`);
    } catch (err) {
      alert('Ошибка обновления кейса');
    } finally {
      setLoading(false);
    }
  };



  return (
    <div className="max-w-3xl mx-auto px-4">
      <h1 className="text-3xl font-bold text-white mb-8">✏️ Редактирование кейса</h1>

      <form onSubmit={handleSubmit} className="glass-card rounded-2xl p-8 space-y-6">
        <div>
          <label className="block text-white/80 mb-2">Заголовок *</label>
          <input
            type="text"
            value={form.title}
            onChange={e => setForm({...form, title: e.target.value})}
            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-orange-500/50"
            required minLength={3}
          />
        </div>

        

        <div>
          <label className="block text-white/80 mb-2">📝 Описание проблемы *</label>
          <textarea
            value={form.symptom_text}
            onChange={e => setForm({...form, symptom_text: e.target.value})}
            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white h-24 focus:outline-none focus:border-orange-500/50 resize-none"
            required minLength={10}
          />
        </div>

        <div>
          <label className="block text-white/80 mb-2">🩺 Диагностика</label>
          <textarea
            value={form.diagnosis}
            onChange={e => setForm({...form, diagnosis: e.target.value})}
            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white h-24 focus:outline-none focus:border-orange-500/50 resize-none"
          />
        </div>

        <div>
          <label className="block text-white/80 mb-2">🛠️ Инструменты</label>
          <input
            type="text"
            value={form.tools_used}
            onChange={e => setForm({...form, tools_used: e.target.value})}
            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-orange-500/50"
          />
        </div>

        <div>
          <label className="block text-white/80 mb-2">Сложность</label>
          <select
            value={form.difficulty}
            onChange={e => setForm({...form, difficulty: e.target.value})}
            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-orange-500/50"
          >
            <option value="easy">🟢 Легко</option>
            <option value="medium">🟡 Средне</option>
            <option value="hard">🔴 Сложно</option>
          </select>
        </div>

        

        <div>
          <label className="block text-white/80 mb-2">📝 Комментарий к изменению</label>
          <input
            type="text"
            value={changeSummary}
            onChange={e => setChangeSummary(e.target.value)}
            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-orange-500/50"
            placeholder="Что изменилось?"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full glass-btn glass-btn-primary py-4 rounded-xl text-lg font-semibold disabled:opacity-50"
        >
          {loading ? 'Сохранение...' : '💾 Сохранить изменения'}
        </button>
        <button
          type="button"
          onClick={() => navigate(`/cases/${id}`)}
          className="w-full py-4 rounded-xl text-lg font-semibold bg-white/5 border border-white/10 text-white/60 hover:text-white hover:bg-white/10 transition mt-2"
        >
          ← Отменить изменения
        </button>
      </form>
    </div>
  );
};

export default CaseEdit;
