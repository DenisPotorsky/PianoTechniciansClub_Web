import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../services/api';

interface Symptom { id: number; name: string; category?: string; }
interface Tag { id: number; name: string; category?: string; }
interface Solution {
  id: number; case_id: number; author_id: number; author_name?: string;
  text: string; tools_used?: string; difficulty: string;
  is_best: boolean; upvotes: number; downvotes: number;
  created_at: string;
}
interface CaseMedia { id: number; media_type: string; url: string; description?: string; }
interface CaseVersion { id: number; version: number; title: string; change_summary?: string; created_at: string; edited_by: number; }

interface CaseData {
  id: number; user_id: number; author_name?: string;
  title: string; description?: string; symptom_text?: string;
  diagnosis?: string; tools_used?: string; difficulty: string;
  is_verified: boolean; view_count: number; helpful_count: number;
  created_at: string; updated_at: string;
  symptoms: Symptom[]; tags: Tag[]; solutions: Solution[]; media: CaseMedia[];
}

const CaseDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [caseData, setCaseData] = useState<CaseData | null>(null);
  const [loading, setLoading] = useState(true);
  const [showVersions, setShowVersions] = useState(false);
  const [versions, setVersions] = useState<CaseVersion[]>([]);
  const [newSolution, setNewSolution] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => { if (id) loadCase(); }, [id]);

  const loadCase = async () => {
    try {
      const res = await api.get(`/cases/${id}`);
      setCaseData(res.data);
    } catch (err) { console.error('Failed to load case'); }
    finally { setLoading(false); }
  };

  const loadVersions = async () => {
    if (!id) return;
    try {
      const res = await api.get(`/cases/${id}/versions`);
      setVersions(res.data);
      setShowVersions(!showVersions);
    } catch (err) { console.error('Failed to load versions'); }
  };

  const submitSolution = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSolution.trim() || !id) return;
    setSubmitting(true);
    try {
      await api.post(`/cases/${id}/solutions/`, { text: newSolution, difficulty: 'medium' });
      setNewSolution('');
      await loadCase();
    } catch (err) { console.error('Failed to submit solution'); }
    finally { setSubmitting(false); }
  };

  const voteSolution = async (solutionId: number, vote: 'up' | 'down') => {
    if (!id) return;
    try {
      await api.post(`/cases/${id}/solutions/${solutionId}/vote?vote=${vote}`);
      await loadCase();
    } catch (err) { console.error('Failed to vote'); }
  };

  if (loading) return <div className="text-white/60 text-center py-12">Загрузка...</div>;
  if (!caseData) return <div className="text-white/60 text-center py-12">Кейс не найден</div>;

  const getDifficultyColor = (d: string) => {
    if (d === 'easy') return 'text-green-400 bg-green-500/10 border-green-500/20';
    if (d === 'hard') return 'text-red-400 bg-red-500/10 border-red-500/20';
    return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20';
  };

  const sortedSolutions = [...caseData.solutions].sort((a, b) => {
    if (a.is_best && !b.is_best) return -1;
    if (!a.is_best && b.is_best) return 1;
    return b.upvotes - a.upvotes;
  });

  return (
    <div className="max-w-4xl mx-auto px-4">
      <Link to="/cases" className="text-white/60 hover:text-orange-300 mb-6 inline-block transition">
        ← Назад к базе знаний
      </Link>

      {/* Заголовок */}
      <div className="glass-card rounded-2xl p-8 mt-4">
        <div className="flex flex-col md:flex-row justify-between items-start gap-4 mb-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              {caseData.is_verified && <span className="text-green-400 text-sm">✓ Проверено</span>}
              <span className={`text-xs px-2 py-0.5 rounded-full border ${getDifficultyColor(caseData.difficulty)}`}>
                {caseData.difficulty === 'easy' ? '🟢 Легко' : caseData.difficulty === 'hard' ? '🔴 Сложно' : '🟡 Средне'}
              </span>
            </div>
            <h1 className="text-3xl font-bold text-white">{caseData.title}</h1>
            {caseData.author_name && (
              <p className="text-white/40 text-sm mt-1">Автор: {caseData.author_name} • {new Date(caseData.created_at).toLocaleDateString('ru-RU')}</p>
            )}
          </div>
          <div className="flex items-center gap-4 text-sm text-white/40">
            <span>👁️ {caseData.view_count}</span>
            {caseData.helpful_count > 0 && <span className="text-green-400">👍 {caseData.helpful_count}</span>}
          </div>
        </div>

        {/* Симптомы */}
        {caseData.symptoms.length > 0 && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-white mb-2">🔍 Симптомы</h2>
            <div className="flex flex-wrap gap-2">
              {caseData.symptoms.map(s => (
                <span key={s.id} className="px-3 py-1 bg-orange-500/10 border border-orange-500/20 rounded-lg text-sm text-orange-300">
                  🔧 {s.name}{s.category ? ` (${s.category})` : ''}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Описание симптома */}
        {caseData.symptom_text && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-white mb-2">📝 Описание проблемы</h2>
            <p className="text-white/80 leading-relaxed">{caseData.symptom_text}</p>
          </div>
        )}

        {/* Диагностика */}
        {caseData.diagnosis && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-white mb-2">🩺 Диагностика</h2>
            <p className="text-white/80 leading-relaxed">{caseData.diagnosis}</p>
          </div>
        )}

        {/* Инструменты */}
        {caseData.tools_used && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-white mb-2">🛠️ Инструменты</h2>
            <p className="text-white/80">{caseData.tools_used}</p>
          </div>
        )}

        {/* Медиа */}
        {caseData.media.length > 0 && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-white mb-3">📸 Фото/Видео</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {caseData.media.map(m => (
                <div key={m.id} className="rounded-xl overflow-hidden bg-black/20">
                  {m.media_type === 'photo' ? (
                    <img src={m.url} alt={m.description || ''} className="w-full h-48 object-cover" />
                  ) : (
                    <video src={m.url} controls className="w-full h-48 object-cover" />
                  )}
                  {m.description && <p className="text-white/60 text-xs p-2">{m.description}</p>}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Теги */}
        {caseData.tags.length > 0 && (
          <div className="pt-6 border-t border-white/10">
            <div className="flex flex-wrap gap-2">
              {caseData.tags.map(t => (
                <span key={t.id} className="px-3 py-1 bg-white/10 rounded-lg text-sm text-white/70">
                  #{t.name}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* История версий */}
        <div className="mt-6 pt-6 border-t border-white/10">
          <button onClick={loadVersions} className="text-white/40 hover:text-white text-sm transition">
            {showVersions ? '▼ Скрыть историю' : '▶ История изменений'}
          </button>
          {showVersions && versions.length > 0 && (
            <div className="mt-3 space-y-2">
              {versions.map(v => (
                <div key={v.id} className="bg-white/5 rounded-lg p-3 text-sm">
                  <span className="text-white/60">v{v.version}</span>
                  <span className="text-white/40 mx-2">•</span>
                  <span className="text-white/80">{v.change_summary}</span>
                  <span className="text-white/30 ml-2">{new Date(v.created_at).toLocaleDateString('ru-RU')}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Решения */}
      <div className="mt-8">
        <h2 className="text-2xl font-bold text-white mb-4">💡 Решения ({caseData.solutions.length})</h2>

        {sortedSolutions.map(sol => (
          <div key={sol.id} className={`glass-card rounded-xl p-6 mb-4 ${sol.is_best ? 'border-green-500/30 bg-green-500/5' : ''}`}>
            {sol.is_best && (
              <div className="text-green-400 text-sm font-semibold mb-2">⭐ Лучшее решение</div>
            )}
            <p className="text-white/90 leading-relaxed whitespace-pre-line mb-4">{sol.text}</p>
            {sol.tools_used && (
              <p className="text-white/60 text-sm mb-3">🛠️ {sol.tools_used}</p>
            )}
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-3">
                <button onClick={() => voteSolution(sol.id, 'up')} className="text-white/40 hover:text-green-400 transition text-sm">
                  👍 {sol.upvotes}
                </button>
                <button onClick={() => voteSolution(sol.id, 'down')} className="text-white/40 hover:text-red-400 transition text-sm">
                  👎 {sol.downvotes}
                </button>
              </div>
              <div className="text-white/40 text-sm">
                {sol.author_name && <span>✍️ {sol.author_name} • </span>}
                {new Date(sol.created_at).toLocaleDateString('ru-RU')}
              </div>
            </div>
          </div>
        ))}

        {/* Форма добавления решения */}
        <div className="glass-card rounded-xl p-6 mt-6">
          <h3 className="text-lg font-semibold text-white mb-3">➕ Ваше решение</h3>
          <form onSubmit={submitSolution}>
            <textarea
              value={newSolution}
              onChange={(e) => setNewSolution(e.target.value)}
              placeholder="Опишите ваше решение..."
              rows={4}
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-white/30 focus:outline-none focus:border-orange-500/50 mb-3 resize-none"
              required
            />
            <button
              type="submit"
              disabled={submitting || !newSolution.trim()}
              className="glass-btn glass-btn-primary px-6 py-2.5 rounded-xl disabled:opacity-50"
            >
              {submitting ? 'Отправка...' : 'Отправить решение'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default CaseDetail;
