import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../services/api';

interface CaseMedia {
  id: number;
  media_type: string;
  url: string;
  description?: string;
}

interface Case {
  id: number;
  title: string;
  symptom: string;
  diagnosis?: string;
  solution: string;
  tools_used?: string;
  difficulty: string;
  is_verified: boolean;
  view_count: number;
  created_at: string;
  tags: string[];
  media: CaseMedia[];
}

const CaseDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [caseData, setCaseData] = useState<Case | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) loadCase();
  }, [id]);

  const loadCase = async () => {
    try {
      const res = await api.get(`/cases/${id}`);
      setCaseData(res.data);
    } catch (err) {
      console.error('Failed to load case');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="text-white text-center py-12">Загрузка...</div>;
  if (!caseData) return <div className="text-white text-center py-12">Кейс не найден</div>;

  const getDifficultyLabel = (d: string) => {
    if (d === 'easy') return '🟢 Легко';
    if (d === 'hard') return '🔴 Сложно';
    return '🟡 Средне';
  };

  return (
    <div className="max-w-4xl mx-auto">
      <Link to="/cases" className="text-white/60 hover:text-white mb-6 inline-block">
        ← Назад к базе знаний
      </Link>

      <div className="glass-card rounded-2xl p-8 mt-4">
        <div className="flex justify-between items-start mb-6">
          <h1 className="text-3xl font-bold text-white">{caseData.title}</h1>
          <div className="flex items-center gap-3">
            {caseData.is_verified && <span className="text-green-500 text-xl" title="Верифицирован">✓</span>}
            <span className="text-white/60">{getDifficultyLabel(caseData.difficulty)}</span>
          </div>
        </div>

        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-semibold text-white mb-3">🔍 Симптом</h2>
            <p className="text-white/80 leading-relaxed">{caseData.symptom}</p>
          </div>

          {caseData.diagnosis && (
            <div>
              <h2 className="text-xl font-semibold text-white mb-3">🩺 Диагностика</h2>
              <p className="text-white/80 leading-relaxed">{caseData.diagnosis}</p>
            </div>
          )}

          <div>
            <h2 className="text-xl font-semibold text-white mb-3">✅ Решение</h2>
            <p className="text-white/80 leading-relaxed whitespace-pre-line">{caseData.solution}</p>
          </div>

          {caseData.tools_used && (
            <div>
              <h2 className="text-xl font-semibold text-white mb-3">🛠️ Инструменты</h2>
              <p className="text-white/80">{caseData.tools_used}</p>
            </div>
          )}

          {caseData.media.length > 0 && (
            <div>
              <h2 className="text-xl font-semibold text-white mb-3">📸 Фото/Видео</h2>
              <div className="grid grid-cols-2 gap-4">
                {caseData.media.map(m => (
                  <div key={m.id} className="rounded-xl overflow-hidden">
                    {m.media_type === 'photo' ? (
                      <img src={m.url} alt={m.description || ''} className="w-full h-48 object-cover" />
                    ) : (
                      <video src={m.url} controls className="w-full h-48 object-cover" />
                    )}
                    {m.description && <p className="text-white/60 text-sm mt-2">{m.description}</p>}
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="flex justify-between items-center pt-6 border-t border-white/10">
            <div className="flex gap-2">
              {caseData.tags.map(tag => (
                <span key={tag} className="px-3 py-1 bg-white/10 rounded-lg text-sm text-white/70">
                  #{tag}
                </span>
              ))}
            </div>
            <span className="text-white/40 text-sm">👁️ {caseData.view_count} просмотров</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CaseDetail;
