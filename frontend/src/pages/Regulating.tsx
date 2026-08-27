import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';

interface RegulatingParam {
  id: number;
  brand: string;
  model: string;
  parameter: string;
  value: string;
  unit: string | null;
}

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

  useEffect(() => {
    loadBrands();
  }, []);

  useEffect(() => {
    loadParams();
  }, [search, selectedBrand]);

  const loadBrands = async () => {
    try {
      const response = await api.get('/regulating/brands');
      setBrands(response.data);
    } catch (error) {
      console.error('Ошибка загрузки брендов:', error);
    }
  };

  const loadParams = async () => {
    setLoading(true);
    try {
      const response = await api.get('/regulating', {
        params: { search, brand: selectedBrand, limit: 200 }
      });
      setParams(response.data);
    } catch (error) {
      console.error('Ошибка загрузки параметров:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await api.post('/regulating/import-csv', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      alert(`✅ Добавлено: ${response.data.added}\n❌ Ошибок: ${response.data.errors?.length || 0}`);
      loadParams();
    } catch (error: any) {
      alert('❌ Ошибка импорта: ' + (error.response?.data?.detail || 'Неизвестная ошибка'));
    }
    e.target.value = '';
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Удалить этот параметр?')) return;
    try {
      await api.delete(`/regulating/${id}`);
      loadParams();
    } catch (error) {
      alert('❌ Ошибка удаления');
    }
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/regulating', null, {
        params: newParam
      });
      alert('✅ Параметр добавлен');
      setShowAddForm(false);
      setNewParam({ brand: '', model: '', parameter: '', value: '', unit: '' });
      loadParams();
    } catch (error) {
      alert('❌ Ошибка добавления');
    }
  };

  return (
    <div className="max-w-7xl mx-auto">
      <div className="glass-card p-4 md:p-6 lg:p-8">
        <div className="text-center mb-6 md:mb-8">
          <div className="text-4xl md:text-5xl mb-3">🔧</div>
          <h2 className="text-2xl md:text-3xl font-bold text-white">
            Регулировочные параметры рояля
          </h2>
          <p className="text-white/50 mt-1 text-sm md:text-base">Технические данные для настройки фортепиано</p>
        </div>

        {/* Поиск и кнопки */}
        <div className="flex flex-col md:flex-row flex-wrap gap-3 md:gap-4 mb-6">
          <input
            type="text"
            placeholder="🔍 Поиск по бренду, модели, параметру..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="glass-input flex-1 min-w-[200px]"
          />
          <select
            value={selectedBrand}
            onChange={(e) => setSelectedBrand(e.target.value)}
            className="glass-input md:w-auto"
          >
            <option value="">Все бренды</option>
            {brands.map((b) => (
              <option key={b} value={b}>{b}</option>
            ))}
          </select>
          {isAdmin && (
            <>
              <label className="glass-btn glass-btn-primary cursor-pointer">
                📤 Импорт CSV
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleImport}
                  className="hidden"
                />
              </label>
              <button
                onClick={() => setShowAddForm(!showAddForm)}
                className="glass-btn"
              >
                {showAddForm ? '❌ Отмена' : '➕ Добавить'}
              </button>
            </>
          )}
        </div>

        {/* Форма добавления */}
        {showAddForm && isAdmin && (
          <form onSubmit={handleAdd} className="glass p-4 md:p-6 rounded-2xl mb-6">
            <h4 className="font-semibold text-white mb-4">➕ Добавление параметра</h4>
            <div className="grid grid-cols-1 md:grid-cols-5 gap-3 md:gap-4">
              <input
                type="text"
                placeholder="Бренд *"
                value={newParam.brand}
                onChange={(e) => setNewParam({ ...newParam, brand: e.target.value })}
                className="glass-input"
                required
              />
              <input
                type="text"
                placeholder="Модель *"
                value={newParam.model}
                onChange={(e) => setNewParam({ ...newParam, model: e.target.value })}
                className="glass-input"
                required
              />
              <input
                type="text"
                placeholder="Параметр *"
                value={newParam.parameter}
                onChange={(e) => setNewParam({ ...newParam, parameter: e.target.value })}
                className="glass-input"
                required
              />
              <input
                type="text"
                placeholder="Значение *"
                value={newParam.value}
                onChange={(e) => setNewParam({ ...newParam, value: e.target.value })}
                className="glass-input"
                required
              />
              <input
                type="text"
                placeholder="Ед. измерения (мм, г...)"
                value={newParam.unit}
                onChange={(e) => setNewParam({ ...newParam, unit: e.target.value })}
                className="glass-input"
              />
            </div>
            <button
              type="submit"
              className="glass-btn glass-btn-primary mt-4"
            >
              ✅ Добавить
            </button>
          </form>
        )}

        {/* Таблица */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-white border-t-transparent"></div>
            <p className="mt-2 text-white/50">Загрузка...</p>
          </div>
        ) : params.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-4xl mb-2">📭</div>
            <p className="text-white/50">Нет данных</p>
            {isAdmin && <p className="text-sm text-white/30 mt-1">Загрузите CSV или добавьте вручную</p>}
          </div>
        ) : (
          <div className="glass-table overflow-x-auto">
            <table className="min-w-full divide-y divide-white/5 text-sm">
              <thead>
                <tr>
                  <th className="px-4 py-3 text-left font-medium text-white/40">Бренд</th>
                  <th className="px-4 py-3 text-left font-medium text-white/40">Модель</th>
                  <th className="px-4 py-3 text-left font-medium text-white/40">Параметр</th>
                  <th className="px-4 py-3 text-left font-medium text-white/40">Значение</th>
                  {isAdmin && <th className="px-4 py-3 text-left font-medium text-white/40">Действия</th>}
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {params.map((p) => (
                  <tr key={p.id} className="hover:bg-white/5 transition">
                    <td className="px-4 py-3 font-medium text-white">{p.brand}</td>
                    <td className="px-4 py-3 text-white/80">{p.model}</td>
                    <td className="px-4 py-3 text-white/80">{p.parameter}</td>
                    <td className="px-4 py-3 font-semibold text-indigo-300">
                      {p.value}
                      {p.unit && <span className="text-white/40 text-xs ml-1">{p.unit}</span>}
                    </td>
                    {isAdmin && (
                      <td className="px-4 py-3">
                        <button
                          onClick={() => handleDelete(p.id)}
                          className="text-red-400 hover:text-red-300 transition font-medium"
                        >
                          🗑️ Удалить
                        </button>
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