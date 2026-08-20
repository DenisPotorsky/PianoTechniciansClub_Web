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

  // Форма для добавления нового параметра
  const [newParam, setNewParam] = useState({
    brand: '',
    model: '',
    parameter: '',
    value: '',
    unit: ''
  });

  const isAdmin = user?.is_admin || user?.is_super_admin;

  // Загружаем список брендов
  useEffect(() => {
    loadBrands();
  }, []);

  // Загружаем параметры при изменении поиска или фильтра
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
        params: {
          search: search || undefined,
          brand: selectedBrand || undefined,
          limit: 200
        }
      });
      setParams(response.data);
    } catch (error) {
      console.error('Ошибка загрузки параметров:', error);
    } finally {
      setLoading(false);
    }
  };

  // Импорт CSV
  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await api.post('/regulating/import-csv', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      alert(`✅ Добавлено: ${response.data.added}\n❌ Ошибок: ${response.data.errors.length}`);
      loadParams();
    } catch (error: any) {
      alert('❌ Ошибка импорта: ' + (error.response?.data?.detail || 'Неизвестная ошибка'));
    }
    e.target.value = '';
  };

  // Добавление параметра
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

  // Удаление параметра
  const handleDelete = async (id: number) => {
    if (!window.confirm('Удалить этот параметр?')) return;
    try {
      await api.delete(`/regulating/${id}`);
      loadParams();
    } catch (error) {
      alert('❌ Ошибка удаления');
    }
  };

  return (
    <div className="max-w-7xl mx-auto">
      <div className="bg-white rounded-3xl shadow-2xl p-8 border border-gray-100">
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">🔧</div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-700 to-indigo-700 bg-clip-text text-transparent">
            Регулировочные параметры рояля
          </h2>
          <p className="text-gray-500 mt-1">Технические данные для настройки фортепиано</p>
        </div>

        {/* Поиск и фильтры */}
        <div className="flex flex-wrap gap-4 mb-6">
          <input
            type="text"
            placeholder="🔍 Поиск по бренду, модели, параметру..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 min-w-[200px] px-4 py-2 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-4 focus:ring-indigo-200 transition-all outline-none"
          />

          <select
            value={selectedBrand}
            onChange={(e) => setSelectedBrand(e.target.value)}
            className="px-4 py-2 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-4 focus:ring-indigo-200 transition-all outline-none"
          >
            <option value="">Все бренды</option>
            {brands.map((b) => (
              <option key={b} value={b}>{b}</option>
            ))}
          </select>

          {/* Кнопки для админов */}
          {isAdmin && (
            <>
              <label className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-xl shadow-md hover:shadow-lg transition-all duration-200 cursor-pointer">
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
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl shadow-md hover:shadow-lg transition-all duration-200"
              >
                {showAddForm ? '❌ Отмена' : '➕ Добавить'}
              </button>
            </>
          )}
        </div>

        {/* Форма добавления */}
        {showAddForm && isAdmin && (
          <form onSubmit={handleAdd} className="mb-6 p-6 bg-gray-50 rounded-2xl border-2 border-gray-200">
            <h4 className="font-semibold text-gray-800 mb-4">➕ Добавление параметра</h4>
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              <input
                type="text"
                placeholder="Бренд *"
                value={newParam.brand}
                onChange={(e) => setNewParam({...newParam, brand: e.target.value})}
                className="px-4 py-2 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-4 focus:ring-indigo-200 transition-all outline-none"
                required
              />
              <input
                type="text"
                placeholder="Модель *"
                value={newParam.model}
                onChange={(e) => setNewParam({...newParam, model: e.target.value})}
                className="px-4 py-2 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-4 focus:ring-indigo-200 transition-all outline-none"
                required
              />
              <input
                type="text"
                placeholder="Параметр *"
                value={newParam.parameter}
                onChange={(e) => setNewParam({...newParam, parameter: e.target.value})}
                className="px-4 py-2 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-4 focus:ring-indigo-200 transition-all outline-none"
                required
              />
              <input
                type="text"
                placeholder="Значение *"
                value={newParam.value}
                onChange={(e) => setNewParam({...newParam, value: e.target.value})}
                className="px-4 py-2 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-4 focus:ring-indigo-200 transition-all outline-none"
                required
              />
              <input
                type="text"
                placeholder="Ед. измерения (мм, г...)"
                value={newParam.unit}
                onChange={(e) => setNewParam({...newParam, unit: e.target.value})}
                className="px-4 py-2 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-4 focus:ring-indigo-200 transition-all outline-none"
              />
            </div>
            <button
              type="submit"
              className="mt-4 px-6 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold rounded-xl shadow-md hover:shadow-lg transition-all duration-200"
            >
              ✅ Добавить
            </button>
          </form>
        )}

        {/* Таблица с данными */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-indigo-600 border-t-transparent"></div>
            <p className="mt-2 text-gray-500">Загрузка...</p>
          </div>
        ) : params.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-4xl mb-2">📭</div>
            <p className="text-gray-500">Нет данных</p>
            {isAdmin && <p className="text-sm text-gray-400 mt-1">Загрузите CSV или добавьте вручную</p>}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">Бренд</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">Модель</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">Параметр</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">Значение</th>
                  {isAdmin && <th className="px-4 py-3 text-left font-medium text-gray-500">Действия</th>}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {params.map((p) => (
                  <tr key={p.id} className="hover:bg-gray-50 transition">
                    <td className="px-4 py-3 font-medium">{p.brand}</td>
                    <td className="px-4 py-3">{p.model}</td>
                    <td className="px-4 py-3">{p.parameter}</td>
                    <td className="px-4 py-3 font-semibold text-indigo-700">
                      {p.value} {p.unit && <span className="text-gray-500 text-xs">{p.unit}</span>}
                    </td>
                    {isAdmin && (
                      <td className="px-4 py-3">
                        <button
                          onClick={() => handleDelete(p.id)}
                          className="text-red-600 hover:text-red-800 transition font-medium"
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