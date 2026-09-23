import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

interface Symptom { id: number; name: string; category?: string; }
interface UploadedMedia { url: string; media_type: string; filename: string; }

const CaseCreate: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [symptoms, setSymptoms] = useState<Symptom[]>([]);
  const [form, setForm] = useState({
    title: '',
    symptom_text: '',
    diagnosis: '',
    solution_text: '',
    tools_used: '',
    difficulty: 'medium',
  });
  const [selectedSymptoms, setSelectedSymptoms] = useState<number[]>([]);
  const [photos, setPhotos] = useState<UploadedMedia[]>([]);
  const [uploading, setUploading] = useState(false);

  useEffect(() => { loadFilters(); }, []);

  const loadFilters = async () => {
    try {
      const symRes = await api.get('/symptoms/');
      setSymptoms(symRes.data);
    } catch (err) { console.error('Failed to load filters'); }
  };

  const toggleSymptom = (id: number) => {
    setSelectedSymptoms(prev => prev.includes(id) ? prev.filter(s => s !== id) : [...prev, id]);
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setUploading(true);
    try {
      for (const file of Array.from(files)) {
        const formData = new FormData();
        formData.append('file', file);
        const res = await api.post('/upload/media', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        setPhotos(prev => [...prev, res.data]);
      }
    } catch (err) {
      alert('Ошибка загрузки файла');
    } finally {
      setUploading(false);
      if (e.target) e.target.value = '';
    }
  };

  const removePhoto = (index: number) => {
    setPhotos(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const caseRes = await api.post('/cases/', {
        ...form,
        symptom_ids: selectedSymptoms,
      });
      const caseId = caseRes.data.id;

      for (const photo of photos) {
        await api.post(`/cases/${caseId}/media`, {
          media_type: photo.media_type,
          url: photo.url,
          description: '',
        });
      }

      navigate(`/cases/${caseId}`);
    } catch (err) {
      alert('Ошибка создания кейса');
    } finally {
      setLoading(false);
    }
  };

  const symptomsByCategory = symptoms.reduce((acc, s) => {
    const cat = s.category || 'другое';
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(s);
    return acc;
  }, {} as Record<string, Symptom[]>);

  return (
    <div className="max-w-3xl mx-auto px-4">
      <h1 className="text-3xl font-bold text-white mb-8">➕ Новый кейс</h1>

      <form onSubmit={handleSubmit} className="glass-card rounded-2xl p-8 space-y-6">
        {/* Заголовок */}
        <div>
          <label className="block text-white/80 mb-2">Заголовок *</label>
          <input
            type="text"
            value={form.title}
            onChange={e => setForm({...form, title: e.target.value})}
            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-orange-500/50"
            required minLength={3}
            placeholder="Например: Западание клавиши Yamaha U3"
          />
        </div>

        {/* Фото */}
        <div>
          <label className="block text-white/80 mb-2">📸 Фото проблемы / решения</label>
          <div className="flex flex-wrap gap-3 mb-3">
            {photos.map((photo, i) => (
              <div key={i} className="relative group">
                <img
                  src={photo.url}
                  alt={`Фото ${i + 1}`}
                  className="w-24 h-24 object-cover rounded-xl border border-white/10"
                />
                <button
                  type="button"
                  onClick={() => removePhoto(i)}
                  className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 rounded-full text-white text-xs flex items-center justify-center opacity-0 group-hover:opacity-100 transition"
                >
                  ✕
                </button>
              </div>
            ))}
            <label className={`w-24 h-24 border-2 border-dashed border-white/20 rounded-xl flex flex-col items-center justify-center cursor-pointer hover:border-orange-500/50 transition ${uploading ? 'opacity-50 pointer-events-none' : ''}`}>
              {uploading ? (
                <span className="text-white/50 text-xs">⏳</span>
              ) : (
                <>
                  <span className="text-2xl text-white/30">+</span>
                  <span className="text-white/30 text-xs mt-1">Фото</span>
                </>
              )}
              <input
                type="file"
                accept="image/jpeg,image/png,image/webp,video/mp4,video/quicktime"
                multiple
                onChange={handleFileUpload}
                className="hidden"
                disabled={uploading}
              />
            </label>
          </div>
          <p className="text-white/30 text-xs">JPG, PNG, WebP, MP4 · до 10 МБ · можно несколько</p>
        </div>

        {/* Симптомы из справочника */}
        {symptoms.length > 0 && (
          <div>
            <label className="block text-white/80 mb-2">🔧 Симптомы проблемы</label>
            <div className="space-y-2">
              {Object.entries(symptomsByCategory).map(([cat, items]) => (
                <div key={cat}>
                  <span className="text-white/40 text-xs uppercase">{cat}</span>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {items.map(s => (
                      <button
                        key={s.id}
                        type="button"
                        onClick={() => toggleSymptom(s.id)}
                        className={`px-3 py-1.5 rounded-lg text-sm border transition ${
                          selectedSymptoms.includes(s.id)
                            ? 'bg-orange-500/20 border-orange-500/40 text-orange-300'
                            : 'bg-white/5 border-white/10 text-white/60 hover:border-white/30'
                        }`}
                      >
                        {s.name}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Описание симптома */}
        <div>
          <label className="block text-white/80 mb-2">📝 Описание проблемы *</label>
          <textarea
            value={form.symptom_text}
            onChange={e => setForm({...form, symptom_text: e.target.value})}
            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white h-24 focus:outline-none focus:border-orange-500/50 resize-none"
            required minLength={10}
            placeholder="Подробное описание: что происходит, когда, при каких условиях..."
          />
        </div>

        {/* Диагностика */}
        <div>
          <label className="block text-white/80 mb-2">🩺 Диагностика</label>
          <textarea
            value={form.diagnosis}
            onChange={e => setForm({...form, diagnosis: e.target.value})}
            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white h-24 focus:outline-none focus:border-orange-500/50 resize-none"
            placeholder="Как выявили причину проблемы"
          />
        </div>

        {/* Решение */}
        <div>
          <label className="block text-white/80 mb-2">✅ Решение *</label>
          <textarea
            value={form.solution_text}
            onChange={e => setForm({...form, solution_text: e.target.value})}
            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white h-32 focus:outline-none focus:border-orange-500/50 resize-none"
            required minLength={10}
            placeholder="Пошаговое описание решения"
          />
        </div>

        {/* Инструменты */}
        <div>
          <label className="block text-white/80 mb-2">🛠️ Инструменты</label>
          <input
            type="text"
            value={form.tools_used}
            onChange={e => setForm({...form, tools_used: e.target.value})}
            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-orange-500/50"
            placeholder="камертон, клинья, войлок..."
          />
        </div>

        {/* Сложность */}
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
