import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';

interface Case {
  id: number;
  title: string;
  symptom: string;
  difficulty: string;
  is_verified: boolean;
  view_count: number;
  created_at: string;
  tags: string[];
}

const CasesList: React.FC = () => {
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCases();
  }, []);

  const loadCases = async () => {
    try {
      const res = await api.get('/cases/');
      setCases(res.data);
    } catch (err) {
      console.error('Failed to load cases');
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyColor = (d: string) => {
    if (d === 'easy') return 'text-green-500';
    if (d === 'hard') return 'text-red-500';
    return 'text-yellow-500';
  };

  if (loading) return <div className="text-white text-center py-12">Загрузка...</div>;

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-white">📚 База знаний</h1>
        <Link to="/cases/new" className="glass-btn glass-btn-primary px-6 py-3 rounded-xl">
          ➕ Добавить кейс
        </Link>
      </div>

      {cases.length === 0 ? (
        <div className="glass-card rounded-2xl p-12 text-center">
          <p className="text-white/60 text-lg">Пока нет кейсов. Будьте первым!</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {cases.map(c => (
            <Link key={c.id} to={`/cases/${c.id}`} className="glass-card rounded-xl p-6 hover:bg-white/5 transition block">
              <div className="flex justify-between items-start mb-3">
                <h2 className="text-xl font-semibold text-white">{c.title}</h2>
                <div className="flex items-center gap-3">
                  {c.is_verified && <span className="text-green-500" title="Верифицирован">✓</span>}
                  <span className={`text-sm ${getDifficultyColor(c.difficulty)}`}>
                    {c.difficulty === 'easy' ? '🟢 Легко' : c.difficulty === 'hard' ? '🔴 Сложно' : '🟡 Средне'}
                  </span>
                </div>
              </div>
              <p className="text-white/70 mb-3 line-clamp-2">{c.symptom}</p>
              <div className="flex justify-between items-center">
                <div className="flex gap-2">
                  {c.tags.slice(0, 3).map(tag => (
                    <span key={tag} className="px-2 py-1 bg-white/10 rounded-lg text-xs text-white/60">
                      {tag}
                    </span>
                  ))}
                </div>
                <span className="text-white/40 text-sm">👁️ {c.view_count}</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

export default CasesList;
