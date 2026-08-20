import React, { useState } from 'react';
import api from '../services/api';
import NumberInput from '../components/NumberInput';

const Calculator: React.FC = () => {
  const [form, setForm] = useState({
    user_id: 1,
    winding_type: 'single',
    core_diameter: 1.2,
    total_diameter: 1.8,
    string_length: 1500,
  });
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await api.post('/calculator/calculate', form);
      setResult(response.data);
    } catch (error) {
      console.error('Ошибка:', error);
      alert('Ошибка при расчете');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="bg-white rounded-3xl shadow-2xl p-8 border border-gray-100">
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">🧮</div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-700 to-indigo-700 bg-clip-text text-transparent">
            Калькулятор басовых струн
          </h2>
          <p className="text-gray-500 mt-1">Расчёт параметров навивки</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5 max-w-lg mx-auto">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Тип навивки</label>
            <select
              value={form.winding_type}
              onChange={(e) => setForm({...form, winding_type: e.target.value})}
              className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-200 transition-all outline-none"
            >
              <option value="single">Одиночная</option>
              <option value="double">Двойная</option>
            </select>
          </div>

          <NumberInput
            label="Диаметр керна (мм)"
            value={form.core_diameter}
            onChange={(val) => setForm({...form, core_diameter: val})}
            placeholder="Например: 1.35 или 1,35"
          />

          <NumberInput
            label="Общий диаметр (мм)"
            value={form.total_diameter}
            onChange={(val) => setForm({...form, total_diameter: val})}
            placeholder="Например: 2.9 или 2,9"
          />

          <NumberInput
            label="Длина струны (мм)"
            value={form.string_length}
            onChange={(val) => setForm({...form, string_length: val})}
            placeholder="Например: 1800.5 или 1800,5"
          />

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-6 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 disabled:opacity-50"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Расчет...
              </span>
            ) : (
              '🧮 Рассчитать'
            )}
          </button>
        </form>

        {result && (
          <div className="mt-8 p-6 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 rounded-2xl border border-blue-200 shadow-lg animate-fadeIn">
            <h3 className="text-xl font-bold text-gray-800 mb-4 text-center">
              📊 Результат расчета
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {result.result.copper_diameter !== undefined && (
                <>
                  <div className="bg-white/80 backdrop-blur p-4 rounded-xl shadow-sm text-center hover:shadow-md transition">
                    <div className="text-sm text-gray-500">Диаметр меди</div>
                    <div className="text-2xl font-bold text-orange-600">
                      {result.result.copper_diameter} <span className="text-sm">мм</span>
                    </div>
                  </div>
                  <div className="bg-white/80 backdrop-blur p-4 rounded-xl shadow-sm text-center hover:shadow-md transition">
                    <div className="text-sm text-gray-500">Длина меди</div>
                    <div className="text-2xl font-bold text-green-600">
                      {result.result.copper_length} <span className="text-sm">мм</span>
                    </div>
                  </div>
                </>
              )}

              {result.result.primary_copper_diameter !== undefined && (
                <>
                  <div className="bg-white/80 backdrop-blur p-4 rounded-xl shadow-sm text-center hover:shadow-md transition">
                    <div className="text-sm text-gray-500">Диаметр первичной меди</div>
                    <div className="text-xl font-bold text-orange-600">
                      {result.result.primary_copper_diameter} мм
                    </div>
                  </div>
                  <div className="bg-white/80 backdrop-blur p-4 rounded-xl shadow-sm text-center hover:shadow-md transition">
                    <div className="text-sm text-gray-500">Диаметр вторичной меди</div>
                    <div className="text-xl font-bold text-purple-600">
                      {result.result.secondary_copper_diameter} мм
                    </div>
                  </div>
                  <div className="bg-white/80 backdrop-blur p-4 rounded-xl shadow-sm text-center hover:shadow-md transition">
                    <div className="text-sm text-gray-500">Длина первичной меди</div>
                    <div className="text-xl font-bold text-green-600">
                      {result.result.primary_copper_length} мм
                    </div>
                  </div>
                  <div className="bg-white/80 backdrop-blur p-4 rounded-xl shadow-sm text-center hover:shadow-md transition">
                    <div className="text-sm text-gray-500">Длина вторичной меди</div>
                    <div className="text-xl font-bold text-green-600">
                      {result.result.secondary_copper_length} мм
                    </div>
                  </div>
                </>
              )}
            </div>

            {result.result.weight_estimate && (
              <div className="mt-4 p-4 bg-yellow-50 border-2 border-yellow-200 rounded-xl text-center">
                <span className="font-semibold text-gray-700">⚖️ Вес меди:</span>
                <span className="ml-2 text-2xl font-bold text-yellow-700">
                  {result.result.weight_estimate} г
                </span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Calculator;