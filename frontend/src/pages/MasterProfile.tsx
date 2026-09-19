import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';

interface Review {
  id: number;
  master_id: number;
  user_id: number;
  first_name: string;
  rating: number;
  text: string;
  created_at: string;
}

interface Master {
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

const MasterProfile: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const [master, setMaster] = useState<Master | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [newRating, setNewRating] = useState(5);
  const [newText, setNewText] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadData();
  }, [id]);

  const loadData = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const [masterRes, reviewsRes] = await Promise.all([
        api.get(`/masters/${id}`),
        api.get(`/masters/${id}/reviews`),
      ]);
      setMaster(masterRes.data);
      setReviews(reviewsRes.data);
    } catch (err) {
      setError('Не удалось загрузить профиль');
    } finally {
      setLoading(false);
    }
  };

  const submitReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user || !id) return;
    setSubmitting(true);
    setError('');
    try {
      await api.post(`/masters/${id}/reviews`, {
        rating: newRating,
        text: newText,
      });
      setNewText('');
      setNewRating(5);
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при отправке отзыва');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div className="p-8 text-white/70">Загрузка...</div>;
  if (!master) return <div className="p-8 text-white/70">Мастер не найден</div>;

  const hasReviewed = user && reviews.some(r => r.user_id === user.id);

  return (
    <div className="min-h-screen p-4 md:p-8 max-w-4xl mx-auto">
      <Link to="/masters" className="text-white/60 hover:text-white mb-4 inline-block">← Назад к карте</Link>

      {/* Profile Card */}
      <div className="glass-card rounded-xl p-6 mb-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-white">
              {master.first_name} {master.last_name || ''}
              {master.is_verified && <span className="ml-2 text-green-400 text-lg">✓ Верифицирован</span>}
            </h1>
            {master.specialization && <p className="text-white/60 mt-1">{master.specialization}</p>}
            {master.city && <p className="text-white/50 mt-1">📍 {master.city}{master.address ? `, ${master.address}` : ''}</p>}
          </div>
          <div className="text-right">
            <div className="text-yellow-400 text-2xl font-bold">⭐ {master.rating.toFixed(1)}</div>
            <div className="text-white/40 text-sm">{master.review_count} отзывов</div>
          </div>
        </div>
        {master.bio && <p className="text-white/70 mt-4 leading-relaxed">{master.bio}</p>}
        <div className="flex gap-4 mt-4 flex-wrap">
          {master.phone && <a href={`tel:${master.phone}`} className="glass-btn glass-btn-primary text-sm">📞 {master.phone}</a>}
          {master.telegram && <a href={`https://t.me/${master.telegram}`} target="_blank" rel="noreferrer" className="glass-btn text-sm">✈️ Telegram</a>}
        </div>
      </div>

      {/* Reviews Section */}
      <h2 className="text-xl font-semibold text-white mb-4">Отзывы ({reviews.length})</h2>

      {/* Add Review Form */}
      {user && !hasReviewed && user.id !== master.user_id && (
        <form onSubmit={submitReview} className="glass-card rounded-xl p-4 mb-6">
          <h3 className="text-white font-medium mb-3">Оставить отзыв</h3>
          <div className="flex gap-2 mb-3">
            {[1, 2, 3, 4, 5].map(star => (
              <button
                key={star}
                type="button"
                onClick={() => setNewRating(star)}
                className={`text-2xl transition ${star <= newRating ? 'text-yellow-400' : 'text-white/30'}`}
              >★</button>
            ))}
          </div>
          <textarea
            value={newText}
            onChange={(e) => setNewText(e.target.value)}
            placeholder="Ваш отзыв..."
            required
            minLength={10}
            rows={3}
            className="w-full glass-card px-4 py-2 text-white placeholder-white/50 border-none outline-none rounded-lg mb-3 resize-none"
          />
          {error && <p className="text-red-400 text-sm mb-2">{error}</p>}
          <button type="submit" disabled={submitting || newText.length < 10} className="glass-btn glass-btn-primary disabled:opacity-50">
            {submitting ? 'Отправка...' : 'Отправить отзыв'}
          </button>
        </form>
      )}

      {user && hasReviewed && <p className="text-white/50 mb-4 italic">Вы уже оставили отзыв этому мастеру</p>}
      {!user && <p className="text-white/50 mb-4"><Link to="/login" className="text-blue-400 underline">Войдите</Link>, чтобы оставить отзыв</p>}

      {/* Reviews List */}
      <div className="space-y-3">
        {reviews.map(review => (
          <div key={review.id} className="glass-card rounded-xl p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-white font-medium">{review.first_name}</span>
              <span className="text-white/40 text-xs">{new Date(review.created_at).toLocaleDateString('ru-RU')}</span>
            </div>
            <div className="text-yellow-400 mb-1">{'★'.repeat(review.rating)}{'☆'.repeat(5 - review.rating)}</div>
            <p className="text-white/70 text-sm">{review.text}</p>
          </div>
        ))}
        {reviews.length === 0 && <p className="text-white/40">Пока нет отзывов</p>}
      </div>
    </div>
  );
};

export default MasterProfile;
