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
  const [error, setError] = useState<string | null>(null);
  const [debugInfo, setDebugInfo] = useState<string>('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    setDebugInfo('');

    try {
      setDebugInfo(`Запрос: POST ${api.defaults.baseURL}/age/detect\nДанные: ${JSON.stringify(form)}`);

      const response = await api.post('/age/detect', form);

      setDebugInfo(prev => prev + `\n\nОтвет (${response.status}): ${JSON.stringify(response.data, null, 2)}`);
      console.log('Ответ сервера:', response.data);

      if (response.data && response.data.detail) {
        setError(response.data.detail);
        return;
      }

      if (response.data && Object.keys(response.data).length > 0) {
        setResult(response.data);
      } else {
        setError('Ничего не найдено. Проверьте бренд и серийный номер.');
      }
    } catch (error: any) {
      console.error('Ошибка:', error);
      setDebugInfo(prev => prev + `\n\nОшибка: ${error.message}\nКод: ${error.response?.status}\nДетали: ${JSON.stringify(error.response?.data)}`);

      if (error.response?.data?.detail) {
        setError(error.response.data.detail);
      } else if (error.response?.data?.message) {
        setError(error.response.data.message);
      } else if (error.code === 'ERR_NETWORK') {
        setError('Ошибка сети. Проверьте подключение к интернету и что бэкенд запущен.');
      } else {
        setError('Ошибка при определении возраста');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="glass-card p-8">
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">🔍</div>
          <h2 className="text-3xl font-bold text-white">
            Возраст инструмента
          </h2>
          <p className="text-white/50 mt-1">Определите год выпуска по бренду и серийному номеру</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5 max-w-lg mx-auto">
          <div>
            <label className="block text-sm font-medium text-white/70 mb-1">Тип бренда</label>
            <select
              value={form.brand_type}
              onChange={(e) => setForm({...form, brand_type: e.target.value})}
              className="glass-select w-full"
            >
              <option value="foreign">🌍 Иностранные</option>
              <option value="russian">🇷🇺 Отечественные</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-white/70 mb-1">Название бренда</label>
            <input
              type="text"
              value={form.brand_name}
              onChange={(e) => setForm({...form, brand_name: e.target.value})}
              placeholder="Например: Steinway, Yamaha, Kawai..."
              className="glass-input w-full"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-white/70 mb-1">Серийный номер</label>
            <input
              type="text"
              inputMode="numeric"
              value={form.serial_number}
              onChange={(e) => setForm({...form, serial_number: e.target.value.replace(/\D/g, '')})}
              placeholder="Введите серийный номер (только цифры)"
              className="glass-input w-full"
            />
          </div>

          <button
            type="submit"
            disabled={loading || !form.brand_name || !form.serial_number}
            className="w-full glass-btn glass-btn-primary py-3 text-lg disabled:opacity-50"
          >
            {loading ? '⏳ Поиск...' : '🔍 Определить возраст'}
          </button>
        </form>

        {error && (
          <div className="mt-6 glass p-5 rounded-2xl text-center border border-red-500/20">
            <div className="text-3xl mb-2">❌</div>
            <p className="text-red-300 font-medium">{error}</p>
            <p className="text-red-300/50 text-sm mt-1">Проверьте правильность ввода</p>
          </div>
        )}

        {result && !error && (
          <div className="mt-8 glass p-6 rounded-2xl animate-fadeIn">
            <h3 className="text-xl font-bold text-white mb-4 text-center">
              🎹 Результат определения
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {result.brand && (
                <div className="glass-card p-4 text-center">
                  <div className="text-sm text-white/50">Бренд</div>
                  <div className="text-xl font-bold text-purple-300">{result.brand}</div>
                </div>
              )}
              {result.country && (
                <div className="glass-card p-4 text-center">
                  <div className="text-sm text-white/50">Страна</div>
                  <div className="text-xl font-bold text-blue-300">{result.country}</div>
                </div>
              )}
              {result.serial_number && (
                <div className="glass-card p-4 text-center">
                  <div className="text-sm text-white/50">Серийный номер</div>
                  <div className="text-xl font-bold text-white">{result.serial_number}</div>
                </div>
              )}
              {result.year && (
                <div className="glass-card p-4 text-center border border-amber-500/20">
                  <div className="text-sm text-white/50">📅 Год выпуска</div>
                  <div className="text-4xl font-bold text-amber-300">{result.year}</div>
                </div>
              )}
            </div>

            {result.info && (
              <div className="mt-4 glass p-4 rounded-xl text-center border border-blue-500/20">
                <span className="font-semibold text-blue-300">ℹ️</span>
                <span className="ml-2 text-white/70">{result.info}</span>
              </div>
            )}
          </div>
        )}

        {debugInfo && (
          <details className="mt-6 glass p-4 rounded-xl">
            <summary className="cursor-pointer text-white/50 text-sm">🔧 Отладка (для разработчика)</summary>
            <pre className="mt-3 p-3 bg-black/30 rounded-lg overflow-auto max-h-60 text-xs text-green-300 whitespace-pre-wrap break-all">
              {debugInfo}
            </pre>
          </details>
        )}
      </div>
    </div>
  );
};

export default AgeDetection;