import React, { useState } from 'react';
import api from '../services/api';

const AgeDetection: React.FC = () => {
  const [form, setForm] = useState({
    brand_name: '',
    brand_type: 'foreign',
    serial_number: '',
  });
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await api.post('/age/detect', form);
      setResult(response.data);
    } catch (error: any) {
      console.error('Ошибка:', error);
      alert(error.response?.data?.detail || 'Ошибка при определении возраста');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="bg-white rounded-3xl shadow-2xl p-8 border border-gray-100">
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">🔍</div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-purple-700 to-pink-700 bg-clip-text text-transparent">
            Возраст инструмента
          </h2>
          <p className="text-gray-500 mt-1">Определите год выпуска по бренду и серийному номеру</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5 max-w-lg mx-auto">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Тип бренда</label>
            <select
              value={form.brand_type}
              onChange={(e) => setForm({...form, brand_type: e.target.value})}
              className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:ring-4 focus:ring-purple-200 transition-all outline-none"
            >
              <option value="foreign">🌍 Иностранные</option>
              <option value="russian">🇷🇺 Отечественные</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Название бренда</label>
            <input
              type="text"
              value={form.brand_name}
              onChange={(e) => setForm({...form, brand_name: e.target.value})}
              placeholder="Например: Steinway, Bechstein, Yamaha..."
              className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:ring-4 focus:ring-purple-200 transition-all outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Серийный номер</label>
            <input
              type="text"
              value={form.serial_number}
              onChange={(e) => setForm({...form, serial_number: e.target.value})}
              placeholder="Введите серийный номер"
              className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:ring-4 focus:ring-purple-200 transition-all outline-none"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-6 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 disabled:opacity-50"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Поиск...
              </span>
            ) : (
              '🔍 Определить возраст'
            )}
          </button>
        </form>

        {result && !result.error && (
          <div className="mt-8 p-6 bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 rounded-2xl border border-purple-200 shadow-lg animate-fadeIn">
            <h3 className="text-xl font-bold text-gray-800 mb-4 text-center">
              🎹 Результат определения
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white/80 backdrop-blur p-4 rounded-xl shadow-sm text-center hover:shadow-md transition">
                <div className="text-sm text-gray-500">Бренд</div>
                <div className="text-xl font-bold text-purple-700">{result.brand}</div>
              </div>
              <div className="bg-white/80 backdrop-blur p-4 rounded-xl shadow-sm text-center hover:shadow-md transition">
                <div className="text-sm text-gray-500">Страна</div>
                <div className="text-xl font-bold text-blue-700">{result.country}</div>
              </div>
              <div className="bg-white/80 backdrop-blur p-4 rounded-xl shadow-sm text-center hover:shadow-md transition">
                <div className="text-sm text-gray-500">Серийный номер</div>
                <div className="text-xl font-bold text-gray-800">{result.serial_number}</div>
              </div>
              <div className="bg-gradient-to-br from-yellow-100 to-amber-50 p-4 rounded-xl shadow-sm text-center border-2 border-yellow-300">
                <div className="text-sm text-gray-600">📅 Год выпуска</div>
                <div className="text-4xl font-bold text-amber-700">{result.year}</div>
              </div>
            </div>

            {result.info && (
              <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-xl text-center">
                <span className="font-semibold text-blue-700">ℹ️</span>
                <span className="ml-2 text-blue-800">{result.info}</span>
              </div>
            )}
          </div>
        )}

        {result?.error && (
          <div className="mt-6 p-5 bg-red-50 border-2 border-red-200 rounded-2xl text-center">
            <div className="text-3xl mb-2">❌</div>
            <p className="text-red-700 font-medium">{result.error}</p>
            <p className="text-red-500 text-sm mt-1">Проверьте правильность ввода</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AgeDetection;