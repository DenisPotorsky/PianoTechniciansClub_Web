import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

interface MasterProfile {
  id: number;
  user_id: number;
  first_name: string;
  last_name?: string;
  specialization?: string;
  city?: string;
  address?: string;
  latitude?: number;
  longitude?: number;
  bio?: string;
  phone?: string;
  telegram?: string;
  photo_url?: string;
  rating: number;
  review_count: number;
  is_verified: boolean;
}

const MasterDashboard: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState<MasterProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);

  const handlePhotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > 2 * 1024 * 1024) { alert('Файл слишком большой (макс. 2 МБ)'); return; }
    setPhotoFile(file);
    setPhotoPreview(URL.createObjectURL(file));
  };

  const uploadPhoto = async () => {
    if (!photoFile) return;
    setUploading(true);
    setError('');
    try {
      const formData = new FormData();
      formData.append('file', photoFile);
      const res = await api.post('/masters/me/photo', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setProfile(prev => prev ? { ...prev, photo_url: res.data.photo_url } : prev);
      setPhotoFile(null);
      setSuccess('✅ Фото загружено!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка загрузки фото');
    } finally {
      setUploading(false);
    }
  };

  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    specialization: '',
    city: '',
    address: '',
    bio: '',
    phone: '',
    telegram: '',
    latitude: '' as string | number,
    longitude: '' as string | number,
  });

  useEffect(() => {
    if (!user) { navigate('/login'); return; }
    loadProfile();
  }, [user]);

  const loadProfile = async () => {
    setLoading(true);
    try {
      const res = await api.get('/masters/me');
      setProfile(res.data);
      setForm({
        first_name: res.data.first_name || '',
        last_name: res.data.last_name || '',
        specialization: res.data.specialization || '',
        city: res.data.city || '',
        address: res.data.address || '',
        bio: res.data.bio || '',
        phone: res.data.phone || '',
        telegram: res.data.telegram || '',
        latitude: res.data.latitude || '',
        longitude: res.data.longitude || '',
      });
      if (res.data.photo_url) setPhotoPreview(res.data.photo_url);
    } catch (err: any) {
      if (err.response?.status === 404) {
        // No profile yet — prefill name from user
        setForm(f => ({ ...f, first_name: user?.first_name || '' }));
      } else {
        setError('Не удалось загрузить профиль');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      const payload = {
        ...form,
        latitude: form.latitude ? Number(form.latitude) : null,
        longitude: form.longitude ? Number(form.longitude) : null,
      };
      const res = await api.put('/masters/me', payload);
      setProfile(res.data);
      setSuccess('✅ Профиль сохранён!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка сохранения');
    } finally {
      setSaving(false);
    }
  };

  const detectLocation = () => {
    if (!navigator.geolocation) { alert('Геолокация не поддерживается'); return; }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setForm(f => ({
          ...f,
          latitude: pos.coords.latitude.toFixed(6),
          longitude: pos.coords.longitude.toFixed(6),
        }));
      },
      () => alert('Не удалось определить местоположение'),
      { enableHighAccuracy: true, timeout: 10000 }
    );
  };

  if (loading) return <div className="p-8 text-white/70">Загрузка...</div>;

  return (
    <div className="min-h-screen p-4 md:p-8 max-w-3xl mx-auto">
      <h1 className="text-2xl md:text-3xl font-bold text-white mb-6">🔧 Кабинет мастера</h1>

      {/* Stats */}
      {profile && (
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="glass-card rounded-xl p-4 text-center">
            <div className="text-yellow-400 text-2xl font-bold">⭐ {profile.rating.toFixed(1)}</div>
            <div className="text-white/50 text-sm">Рейтинг</div>
          </div>
          <div className="glass-card rounded-xl p-4 text-center">
            <div className="text-white text-2xl font-bold">{profile.review_count}</div>
            <div className="text-white/50 text-sm">Отзывов</div>
          </div>
          <div className="glass-card rounded-xl p-4 text-center">
            <div className={`text-2xl font-bold ${profile.is_verified ? 'text-green-400' : 'text-white/40'}`}>
              {profile.is_verified ? '✓' : '—'}
            </div>
            <div className="text-white/50 text-sm">Верификация</div>
          </div>
        </div>
      )}


      {/* Photo */}
      <div className="glass-card rounded-xl p-6 mb-6 flex items-center gap-6">
        <div className="w-24 h-24 rounded-full overflow-hidden bg-white/10 flex-shrink-0 flex items-center justify-center">
          {photoPreview ? (
            <img src={photoPreview} alt="Фото" className="w-full h-full object-cover" />
          ) : (
            <span className="text-white/30 text-3xl">👤</span>
          )}
        </div>
        <div className="flex-1">
          <h3 className="text-white font-medium mb-2">Фото профиля</h3>
          <div className="flex gap-2 items-center">
            <label className="glass-btn text-sm cursor-pointer">
              📷 Выбрать фото
              <input type="file" accept="image/jpeg,image/png,image/webp" onChange={handlePhotoChange} className="hidden" />
            </label>
            {photoFile && (
              <button onClick={uploadPhoto} disabled={uploading} className="glass-btn glass-btn-primary text-sm disabled:opacity-50">
                {uploading ? 'Загрузка...' : '⬆️ Загрузить'}
              </button>
            )}
          </div>
          <p className="text-white/40 text-xs mt-2">JPEG, PNG или WebP, макс. 2 МБ</p>
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSave} className="glass-card rounded-xl p-6 space-y-4">
        <h2 className="text-lg font-semibold text-white mb-2">Профиль</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-white/70 mb-1">Имя *</label>
            <input type="text" required value={form.first_name} onChange={e => setForm({...form, first_name: e.target.value})} className="glass-input w-full" />
          </div>
          <div>
            <label className="block text-sm text-white/70 mb-1">Фамилия</label>
            <input type="text" value={form.last_name} onChange={e => setForm({...form, last_name: e.target.value})} className="glass-input w-full" />
          </div>
        </div>

        <div>
          <label className="block text-sm text-white/70 mb-1">Специализация</label>
          <input type="text" placeholder="настройка, регулировка, ремонт..." value={form.specialization} onChange={e => setForm({...form, specialization: e.target.value})} className="glass-input w-full" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-white/70 mb-1">Город</label>
            <input type="text" value={form.city} onChange={e => setForm({...form, city: e.target.value})} className="glass-input w-full" />
          </div>
          <div>
            <label className="block text-sm text-white/70 mb-1">Адрес / район</label>
            <input type="text" value={form.address} onChange={e => setForm({...form, address: e.target.value})} className="glass-input w-full" />
          </div>
        </div>

        <div>
          <label className="block text-sm text-white/70 mb-1">Координаты (для карты)</label>
          <div className="flex gap-2">
            <input type="number" step="any" placeholder="Широта" value={form.latitude} onChange={e => setForm({...form, latitude: e.target.value})} className="glass-input flex-1" />
            <input type="number" step="any" placeholder="Долгота" value={form.longitude} onChange={e => setForm({...form, longitude: e.target.value})} className="glass-input flex-1" />
            <button type="button" onClick={detectLocation} className="glass-btn glass-btn-primary whitespace-nowrap">📍 Определить</button>
          </div>
        </div>

        <div>
          <label className="block text-sm text-white/70 mb-1">О себе</label>
          <textarea rows={3} value={form.bio} onChange={e => setForm({...form, bio: e.target.value})} className="glass-input w-full resize-none" placeholder="Опыт работы, специализация на инструментах..." />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-white/70 mb-1">Телефон</label>
            <input type="tel" value={form.phone} onChange={e => setForm({...form, phone: e.target.value})} className="glass-input w-full" placeholder="+7..." />
          </div>
          <div>
            <label className="block text-sm text-white/70 mb-1">Telegram</label>
            <input type="text" value={form.telegram} onChange={e => setForm({...form, telegram: e.target.value})} className="glass-input w-full" placeholder="@username" />
          </div>
        </div>

        {error && <p className="text-red-400 text-sm">{error}</p>}
        {success && <p className="text-green-400 text-sm">{success}</p>}

        <button type="submit" disabled={saving} className="glass-btn glass-btn-primary w-full disabled:opacity-50">
          {saving ? 'Сохранение...' : '💾 Сохранить профиль'}
        </button>
      </form>

      {profile && (
        <div className="mt-6 text-center">
          <a href={`/masters/${profile.id}`} className="text-blue-400 hover:underline text-sm">Посмотреть свой профиль на карте →</a>
        </div>
      )}
    </div>
  );
};

export default MasterDashboard;
