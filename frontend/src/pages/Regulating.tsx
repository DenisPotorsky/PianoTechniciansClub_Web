import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface RegulatingParam {
  id: number;
  brand: string;
  model: string;
  parameter: string;
  value: string;
  unit: string | null;
}

const API = '/api/v1';

const Regulating: React.FC = () => {
  const { user } = useAuth();
  const [params, setParams] = useState<RegulatingParam[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [brands, setBrands] = useState<string[]>([]);
  const [selectedBrand, setSelectedBrand] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [newParam, setNewParam] = useState({
    brand: '',
    model: '',
    parameter: '',
    value: '',
    unit: ''
  });

  const isAdmin = user?.is_admin || user?.is_super_admin;

  const getToken = () => localStorage.getItem('token') || localStorage.getItem('access_token');

  const fetchData = async (url: string) => {
    const res = await fetch(url, {
      headers: { 'Authorization': 'Bearer ' + getToken(), 'Content-Type': 'application/json' }
    });
    if (!res.ok) throw new Error('Ошибка ' + res.status);
    return res.json();
  };

  const postData = async (url: string, body?: any) => {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Authorization': 'Bearer ' + getToken(), 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined
    });
    if (!res.ok) throw new Error('Ошибка ' + res.status);
    return res.json();
  };

  const deleteData = async (url: string) => {
    const res = await fetch(url, {
      method: 'DELETE',
      headers: { 'Authorization': 'Bearer ' + getToken() }
    });
    if (!res.ok) throw new Error('Ошибка ' + res.status);
  };

  useEffect(() => { loadBrands(); }, []);
  useEffect(() => { loadParams(); }, [search, selectedBrand]);

  const loadBrands = async () => {
    try {
      const data = await fetchData(API + '/regulating/brands');
      setBrands(data);
    } catch (e) { console.error(e); }
  };

  const loadParams = async () => {
    setLoading(true);
    try {
      const data = await fetchData(API + '/regulating/?search=' + search + '&brand=' + selectedBrand + '&limit=200');
      setParams(data);
    } catch (e) { console.error('Ошибка загрузки параметров:', e); }
    finally { setLoading(false); }
  };

  const handleImportCSV = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await fetch(API + '/regulating/import-csv', {
        method: 'POST',
        headers: { 'Authorization': 'Bearer ' + getToken() },
        body: formData
      });
      if (res.ok) { loadParams(); loadBrands(); }
    } catch (e) { console.error(e); }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Удалить параметр?')) return;
    try { await deleteData(API + '/regulating/' + id); loadParams(); }
    catch (e) { console.error(e); }
  };

  const handleAdd = async () => {
    try {
      await postData(API + '/regulating', newParam);
      setShowAddForm(false);
      setNewParam({ brand: '', model: '', parameter: '', value: '', unit: '' });
      loadParams(); loadBrands();
    } catch (e) { console.error(e); }
  };

  return (
    <div className="min-h-screen p-4 md:p-8">
      {/* Прозрачная карточка как во всём проекте */}
      <div className="glass-card p-6 md:p-8 max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <span className="text-4xl">🔧</span>
          <h1 className="text-2xl md:text-3xl font-bold mt-2 text-white drop-shadow-lg">Регулировочные параметры рояля</h1>
          <p className="text-white/70 mt-1 drop-shadow">Технические данные для настройки фортепиано</p>
        </div>

        <div className="flex flex-wrap gap-3 mb-6">
          <input
            type="text"
            placeholder=" Поиск по бренду, модели, параметру..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 min-w-[200px] bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg px-4 py-2 text-white placeholder-white/50 focus:outline-none focus:border-white/40"
          />
          <select
            value={selectedBrand}
            onChange={(e) => setSelectedBrand(e.target.value)}
            className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-white/40"
          >
            <option value="" className="bg-gray-800">Все бренды</option>
            {brands.map(b => <option key={b} value={b} className="bg-gray-800">{b}</option>)}
          </select>
          {isAdmin && (
            <>
              <label className="bg-purple-600/80 hover:bg-purple-600 backdrop-blur-sm px-4 py-2 rounded-lg cursor-pointer text-sm text-white border border-white/10">
                📁 Импорт CSV
                <input type="file" accept=".csv" onChange={handleImportCSV} className="hidden" />
              </label>
              <button onClick={() => setShowAddForm(!showAddForm)} className="bg-white/10 hover:bg-white/20 backdrop-blur-sm px-4 py-2 rounded-lg text-sm text-white border border-white/10">
                + Добавить
              </button>
            </>
          )}
        </div>

        {showAddForm && (
          <div className="bg-black/30 backdrop-blur-sm rounded-lg p-4 mb-6 grid grid-cols-1 md:grid-cols-5 gap-3 border border-white/10">
            <input placeholder="Бренд" value={newParam.brand} onChange={e => setNewParam({...newParam, brand: e.target.value})} className="bg-black/30 border border-white/20 rounded px-3 py-2 text-white placeholder-white/40" />
            <input placeholder="Модель" value={newParam.model} onChange={e => setNewParam({...newParam, model: e.target.value})} className="bg-black/30 border border-white/20 rounded px-3 py-2 text-white placeholder-white/40" />
            <input placeholder="Параметр" value={newParam.parameter} onChange={e => setNewParam({...newParam, parameter: e.target.value})} className="bg-black/30 border border-white/20 rounded px-3 py-2 text-white placeholder-white/40" />
            <input placeholder="Значение" value={newParam.value} onChange={e => setNewParam({...newParam, value: e.target.value})} className="bg-black/30 border border-white/20 rounded px-3 py-2 text-white placeholder-white/40" />
            <div className="flex gap-2">
              <input placeholder="Ед." value={newParam.unit} onChange={e => setNewParam({...newParam, unit: e.target.value})} className="bg-black/30 border border-white/20 rounded px-3 py-2 text-white placeholder-white/40 w-20" />
              <button onClick={handleAdd} className="bg-green-600/80 hover:bg-green-600 px-4 py-2 rounded text-sm text-white">✓</button>
            </div>
          </div>
        )}

        {loading ? (
          <div className="text-center py-12 text-white/60">⏳ Загрузка...</div>
        ) : params.length === 0 ? (
          <div className="text-center py-12 text-white/60">
            <span className="text-4xl">📭</span>
            <p className="mt-2">Нет данных</p>
            <p className="text-sm">Загрузите CSV или добавьте вручную</p>
          </div>
        ) : (
          <div className="overflow-x-auto rounded-xl border border-white/10">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-black/40 backdrop-blur-sm">
                  <th className="text-left py-3 px-4 font-semibold text-white/90">Бренд</th>
                  <th className="text-left py-3 px-4 font-semibold text-white/90">Модель</th>
                  <th className="text-left py-3 px-4 font-semibold text-white/90">Параметр</th>
                  <th className="text-right py-3 px-4 font-semibold text-white/90">Значение</th>
                  <th className="text-left py-3 px-4 font-semibold text-white/90">Ед.</th>
                  {isAdmin && <th className="py-3 px-4"></th>}
                </tr>
              </thead>
              <tbody>
                {params.map((p, i) => (
                  <tr key={p.id} className={i % 2 === 0 ? 'bg-black/20' : 'bg-black/10'}>
                    <td className="py-3 px-4 text-cyan-300 font-medium drop-shadow">{p.brand}</td>
                    <td className="py-3 px-4 text-white/80 drop-shadow">{p.model}</td>
                    <td className="py-3 px-4 text-white drop-shadow">{p.parameter}</td>
                    <td className="py-3 px-4 text-right font-mono text-yellow-300 font-bold text-base drop-shadow-lg">{p.value}</td>
                    <td className="py-3 px-4 text-white/60 drop-shadow">{p.unit || '—'}</td>
                    {isAdmin && (
                      <td className="py-3 px-4">
                        <button onClick={() => handleDelete(p.id)} className="text-red-400 hover:text-red-300 text-xs drop-shadow">🗑</button>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Regulating;
