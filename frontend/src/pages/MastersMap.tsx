import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import api from '../services/api';

// Fix for default marker icons in react-leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

interface Master {
  id: number;
  user_id: number;
  first_name: string;
  last_name?: string;
  specialization?: string;
  city?: string;
  latitude?: number;
  longitude?: number;
  bio?: string;
  phone?: string;
  rating: number;
  distance_km?: number;
  review_count: number;
  is_verified: boolean;
}

const MastersMap: React.FC = () => {
  const [masters, setMasters] = useState<Master[]>([]);
  const [loading, setLoading] = useState(true);

  const [userLat, setUserLat] = useState<number | null>(null);
  const [userLng, setUserLng] = useState<number | null>(null);
  const [radiusKm, setRadiusKm] = useState<number>(50);
  const [geoLoading, setGeoLoading] = useState(false);

  const findNearby = () => {
    if (!navigator.geolocation) { alert('Геолокация не поддерживается'); return; }
    setGeoLoading(true);
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;
        setUserLat(lat);
        setUserLng(lng);
        try {
          const res = await api.get('/masters/', { params: { lat, lng, radius_km: radiusKm } });
          setMasters(res.data);

        } catch (err) { console.error(err); }
        finally { setGeoLoading(false); }
      },
      (err) => { alert('Не удалось определить местоположение'); setGeoLoading(false); },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  };

  const clearGeoFilter = () => {
    setUserLat(null);
    setUserLng(null);
    loadMasters();
  };

  const [filterCity, setFilterCity] = useState('');

  useEffect(() => {
    loadMasters();
  }, [filterCity]);

  const loadMasters = async () => {
    setLoading(true);
    try {
      const params = filterCity ? { city: filterCity } : {};
      const res = await api.get('/masters/', { params });
      setMasters(res.data);
    } catch (err) {
      console.error('Failed to load masters:', err);
    } finally {
      setLoading(false);
    }
  };

  const mastersWithCoords = masters.filter(m => m.latitude && m.longitude);

  return (
    <div className="min-h-screen p-4 md:p-8">
      <h1 className="text-3xl font-bold text-white mb-6">🗺️ Карта мастеров</h1>

      {/* Filters */}
      <div className="flex gap-3 mb-6 flex-wrap">
        <input
          type="text"
          placeholder="Фильтр по городу..."
          value={filterCity}
          onChange={(e) => setFilterCity(e.target.value)}
          className="glass-card px-4 py-2 text-white placeholder-white/50 border-none outline-none rounded-lg w-full md:w-64"
        />
      </div>

      {/* Map */}
      <div className="glass-card rounded-xl overflow-hidden h-[500px] mb-8">
        {loading ? (
          <div className="flex items-center justify-center h-full text-white/70">Загрузка...</div>
        ) : mastersWithCoords.length === 0 ? (
          <div className="flex items-center justify-center h-full text-white/70">
            Нет мастеров с координатами
          </div>
        ) : (
          <MapContainer
            center={[55.7558, 37.6173]}
            zoom={5}
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
                        {userLat !== null && userLng !== null && (
              <Marker position={[userLat, userLng]} icon={L.divIcon({className: 'user-marker', html: '<div style="background:#3b82f6;width:16px;height:16px;border-radius:50%;border:3px solid white;box-shadow:0 0 8px rgba(59,130,246,0.6);"></div>', iconSize: [16,16], iconAnchor: [8,8]})}>
                <Popup><div className="text-sm font-bold">📍 Вы здесь</div></Popup>
              </Marker>
            )}
            {mastersWithCoords.map((master) => (
              <Marker key={master.id} position={[master.latitude!, master.longitude!]}>
                <Popup>
                  <div className="text-sm min-w-[180px]">
                    <div className="font-bold text-base mb-1">
                      <a href="/masters/{master.id}" style={{color:'inherit',textDecoration:'underline'}}>{master.first_name} {master.last_name || ''}</a>
                      {master.is_verified && <span className="ml-1 text-green-600" title="Верифицирован">✓</span>}
                    </div>
                    {master.specialization && <div className="text-gray-600 mb-1">{master.specialization}</div>}
                    {master.city && <div className="text-gray-500 mb-1">📍 {master.city}</div>}
                    {master.distance_km !== undefined && <div className="text-blue-600 font-medium mb-1">📏 {master.distance_km} км от вас</div>}
                    <div className="mb-1">⭐ {master.rating.toFixed(1)} ({master.review_count} отзывов)</div>
                    {master.phone && <div className="text-gray-600">📞 {master.phone}</div>}
                    {master.bio && <div className="text-gray-500 mt-1 text-xs line-clamp-2">{master.bio}</div>}
                  </div>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        )}
      </div>

      {/* List */}
      <h2 className="text-xl font-semibold text-white mb-4">Список мастеров ({masters.length})</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {masters.map((master) => (
          <div key={master.id} className="glass-card p-4 rounded-xl">
            <div className="flex items-start justify-between mb-2">
              <div>
                <h3 className="text-white font-semibold text-lg">
                  {master.first_name} {master.last_name || ''}
                  {master.is_verified && <span className="ml-2 text-green-400 text-sm" title="Верифицирован">✓ Верифицирован</span>}
                </h3>
                {master.specialization && <p className="text-white/60 text-sm">{master.specialization}</p>}
              </div>
              <div className="text-right">
                <div className="text-yellow-400 font-bold">⭐ {master.rating.toFixed(1)}</div>
                {master.distance_km !== undefined && <div className="text-blue-400 text-sm mt-1">📏 {master.distance_km} км</div>}
                <div className="text-white/40 text-xs">{master.review_count} отзывов</div>
              </div>
            </div>
            {master.city && <p className="text-white/50 text-sm mb-1">📍 {master.city}</p>}
            {master.phone && <p className="text-white/50 text-sm mb-1">📞 {master.phone}</p>}
            {master.bio && <p className="text-white/40 text-xs mt-2 line-clamp-2">{master.bio}</p>}
          </div>
        ))}
      </div>
    </div>
  );
};

export default MastersMap;
