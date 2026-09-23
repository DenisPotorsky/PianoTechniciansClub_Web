import React, { useState, useEffect } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

interface Symptom {
  id: number;
  name: string;
  category?: string;
}

interface Tag {
  id: number;
  name: string;
  category?: string;
}

interface CaseItem {
  id: number;
  title: string;
  symptom_text?: string;
  difficulty: string;
  is_verified: boolean;
  view_count: number;
  helpful_count: number;
  created_at: string;
  author_name?: string;
  symptoms: Symptom[];
  tags: Tag[];
  solutions_count: number;
  status?: string;
  user_id?: number;
}

const CasesList: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [cases, setCases] = useState<CaseItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [symptoms, setSymptoms] = useState<Symptom[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);

  const [search, setSearch] = useState(searchParams.get('search') || '');
  const [symptomFilter, setSymptomFilter] = useState(searchParams.get('symptom_id') || '');
  const [tagFilter, setTagFilter] = useState(searchParams.get('tag_id') || '');
  const [difficultyFilter, setDifficultyFilter] = useState(searchParams.get('difficulty') || '');
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    loadFilters();
  }, []);

  useEffect(() => {
    loadCases();
  }, [searchParams]);

  const loadFilters = async () => {
    try {
      const [symRes, tagRes] = await Promise.all([
        api.get('/symptoms/'),
        api.get('/tags/'),
      ]);
      setSymptoms(symRes.data);
      setTags(tagRes.data);
    } catch (err) {
      console.error('Failed to load filters');
    }
  };

  const loadCases = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      const s = searchParams.get('search');
      const si = searchParams.get('symptom_id');
      const ti = searchParams.get('tag_id');
      const d = searchParams.get('difficulty');
      if (s) params.set('search', s);
      if (si) params.set('symptom_id', si);
      if (ti) params.set('tag_id', ti);
      if (d) params.set('difficulty', d);

      const res = await api.get(`/cases/?${params.toString()}`);
      setCases(res.data.items || []);
      setTotal(res.data.total || 0);
    } catch (err) {
      console.error('Failed to load cases');
    } finally {
      setLoading(false);
    }
  };

  const updateFilter = (key: string, value: string) => {
    const params = new URLSearchParams(searchParams);
    if (value) {
      params.set(key, value);
    } else {
      params.delete(key);
    }
    setSearchParams(params);
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    updateFilter('search', search);
  };

  const getDifficultyColor = (d: string) => {
    if (d === 'easy') return 'text-green-400 bg-green-500/10 border-green-500/20';
    if (d === 'hard') return 'text-red-400 bg-red-500/10 border-red-500/20';
    return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20';
  };

  const getDifficultyLabel = (d: string) => {
    if (d === 'easy') return '🟢 Легко';
    if (d === 'hard') return '🔴 Сложно';
    return '🟡 Средне';
  };

  return (
    <div className="max-w-6xl mx-auto px-4">
      {/* Заголовок */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white">📚 База знаний</h1>
          <p className="text-white/50 mt-1">{total} кейсов в базе</p>
        </div>
        <Link to="/cases/new" className="glass-btn glass-btn-primary px-6 py-3 rounded-xl whitespace-nowrap">
          ➕ Добавить кейс
        </Link>
      </div>

      {/* Фильтры */}
      <div className="glass-card rounded-2xl p-4 mb-6 space-y-3">
        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            type="text"
            placeholder="🔍 Поиск по заголовку или симптому..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white placeholder-white/30 focus:outline-none focus:border-orange-500/50"
          />
          <button type="submit" className="glass-btn glass-btn-primary px-5 py-2.5 rounded-xl">
            Найти
          </button>
        </form>

        <div className="flex flex-wrap gap-3">
          <select
            value={symptomFilter}
            onChange={(e) => { setSymptomFilter(e.target.value); updateFilter('symptom_id', e.target.value); }}
            className="bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-white text-sm focus:outline-none focus:border-orange-500/50"
          >
            <option value="">Все симптомы</option>
            {symptoms.map(s => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>

          <select
            value={tagFilter}
            onChange={(e) => { setTagFilter(e.target.value); updateFilter('tag_id', e.target.value); }}
            className="bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-white text-sm focus:outline-none focus:border-orange-500/50"
          >
            <option value="">Все теги</option>
            {tags.map(t => (
              <option key={t.id} value={t.id}>{t.name}{t.category ? ` (${t.category})` : ''}</option>
            ))}
          </select>

          <select
            value={difficultyFilter}
            onChange={(e) => { setDifficultyFilter(e.target.value); updateFilter('difficulty', e.target.value); }}
            className="bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-white text-sm focus:outline-none focus:border-orange-500/50"
          >
            <option value="">Любая сложность</option>
            <option value="easy">🟢 Легко</option>
            <option value="medium">🟡 Средне</option>
            <option value="hard">🔴 Сложно</option>
          </select>

          {(search || symptomFilter || tagFilter || difficultyFilter) && (
            <button
              onClick={() => {
                setSearch(''); setSymptomFilter(''); setTagFilter(''); setDifficultyFilter('');
                setSearchParams({});
              }}
              className="text-white/40 hover:text-white text-sm px-3 py-2"
            >
              ✕ Сбросить
            </button>
          )}
        </div>
      </div>

      {/* Список */}
      {loading ? (
        <div className="text-white/60 text-center py-12">Загрузка...</div>
      ) : cases.length === 0 ? (
        <div className="glass-card rounded-2xl p-12 text-center">
          <p className="text-white/60 text-lg">Кейсы не найдены 😔</p>
          <p className="text-white/40 text-sm mt-2">Попробуйте изменить фильтры или добавьте новый кейс</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {cases.map(c => (
            <Link
              key={c.id}
              to={`/cases/${c.id}`}
              className="glass-card rounded-xl p-6 hover:bg-white/5 transition block group"
            >
              <div className="flex justify-between items-start mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                    {c.status === 'published' ? (
                      <span className="text-xs px-2 py-0.5 rounded-full border text-green-400 bg-green-500/10 border-green-500/20">✅ Опубликовано</span>
                    ) : (
                      <span className="text-xs px-2 py-0.5 rounded-full border text-yellow-400 bg-yellow-500/10 border-yellow-500/20">📝 Черновик</span>
                    )}
                    {c.is_verified && <span className="text-green-400 text-sm" title="Верифицирован">✓ Проверено</span>}
                    <span className={`text-xs px-2 py-0.5 rounded-full border ${getDifficultyColor(c.difficulty)}`}>
                      {getDifficultyLabel(c.difficulty)}
                    </span>
                  </div>
                  <h2 className="text-xl font-semibold text-white group-hover:text-orange-300 transition">
                    {c.title}
                  </h2>
                </div>
                {(user?.id === c.user_id || user?.is_admin) && (
                  <div className="flex gap-1 ml-2 shrink-0">
                    <Link to={`/cases/${c.id}/edit`} onClick={e => e.stopPropagation()} className="px-2 py-1 rounded-lg text-xs bg-blue-500/20 border border-blue-500/30 text-blue-300 hover:bg-blue-500/30 transition">✏️</Link>
                    <button onClick={async (e) => { e.stopPropagation(); e.preventDefault(); if(confirm('Удалить кейс?')){ try{ await api.delete(`/cases/${c.id}`); loadCases(); }catch{alert('Ошибка')} }}} className="px-2 py-1 rounded-lg text-xs bg-red-500/20 border border-red-500/30 text-red-300 hover:bg-red-500/30 transition">🗑️</button>
                  </div>
                )}
              </div>

              {c.symptom_text && (
                <p className="text-white/70 mb-3 line-clamp-2">{c.symptom_text}</p>
              )}

              <div className="flex flex-wrap justify-between items-center gap-2">
                <div className="flex flex-wrap gap-2">
                  {c.symptoms.map(s => (
                    <span key={s.id} className="px-2 py-1 bg-orange-500/10 border border-orange-500/20 rounded-lg text-xs text-orange-300">
                      🔧 {s.name}
                    </span>
                  ))}
                  {c.tags.slice(0, 3).map(t => (
                    <span key={t.id} className="px-2 py-1 bg-white/10 rounded-lg text-xs text-white/60">
                      {t.name}
                    </span>
                  ))}
                </div>

                <div className="flex items-center gap-4 text-sm text-white/40">
                  {c.solutions_count > 0 && (
                    <span>💡 {c.solutions_count} реш.</span>
                  )}
                  {c.helpful_count > 0 && (
                    <span className="text-green-400">👍 {c.helpful_count}</span>
                  )}
                  <span>👁️ {c.view_count}</span>
                  {c.author_name && (
                    <span className="text-white/30">✍️ {c.author_name}</span>
                  )}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

export default CasesList;
