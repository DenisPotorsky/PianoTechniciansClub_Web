import React, { useState } from 'react';
import api from '../services/api';

const Calculator: React.FC = () => {
  const [form, setForm] = useState({
    user_id: 1,
    winding_type: 'single',
    core_diameter: '1.2',
    total_diameter: '1.8',
    string_length: '1500',
  });
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  // Функция для преобразования запятой в точку
  const normalizeNumber = (value: string): string => {
    // Заменяем запятую на точку
    return value.replace(',', '.');
  };

  // Функция для парсинга числа
  const parseNumber = (value: string): number => {
    const normalized = normalizeNumber(value);
    const parsed = parseFloat(normalized);
    return isNaN(parsed) ? 0 : parsed;
  };

  // Функция для валидации поля
  const validateField = (name: string, value: string): string => {
    if (value.trim() === '') {
      return 'Поле обязательно для заполнения';
    }
    const num = parseNumber(value);
    if (isNaN(num) || num <= 0) {
      return 'Введите положительное число';
    }
    return '';
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;

    // Обновляем значение
    setForm({ ...form, [name]: value });

    // Проверяем ошибку
    const error = validateField(name, value);
    setErrors({ ...errors, [name]: error });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Проверяем все поля
    const newErrors: { [key: string]: string } = {};
    let hasError = false;

    ['core_diameter', 'total_diameter', 'string_length'].forEach((field) => {
      const value = form[field as keyof typeof form] as string;
      const error = validateField(field, value);
      if (error) {
        newErrors[field] = error;
        hasError = true;
      }
    });

    if (hasError) {
      setErrors(newErrors);
      return;
    }

    // Подготавливаем данные для отправки
    const payload = {
      user_id: form.user_id,
      winding_type: form.winding_type,
      core_diameter: parseNumber(form.core_diameter),
      total_diameter: parseNumber(form.total_diameter),
      string_length: parseNumber(form.string_length),
    };

    setLoading(true);
    try {
      const response = await api.post('/calculator/calculate', payload);

      if (response.data && response.data.result) {
        setResult(response.data.result);
      } else {
        setResult(response.data);
      }
    } catch (error) {
      console.error('Ошибка:', error);
      alert('Ошибка при расчете');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="glass-card p-8">
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">🧮</div>
          <h2 className="text-3xl font-bold text-white">
            Калькулятор басовых струн
          </h2>
          <p className="text-white/50 mt-1">Расчёт параметров навивки</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5 max-w-lg mx-auto">
          <div>
            <label className="block text-sm font-medium text-white/70 mb-1">Тип навивки</label>
            <select
              value={form.winding_type}
              onChange={(e) => setForm({...form, winding_type: e.target.value})}
              className="glass-select w-full"
            >
              <option value="single">Одиночная</option>
              <option value="double">Двойная</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-white/70 mb-1">
              Диаметр керна (мм)
            </label>
            <input
              type="text"
              name="core_diameter"
              value={form.core_diameter}
              onChange={handleInputChange}
              placeholder="Например: 1.35 или 1,35"
              className={`glass-input w-full ${errors.core_diameter ? 'border-red-500/50' : ''}`}
            />
            {errors.core_diameter && (
              <p className="text-red-400 text-xs mt-1">{errors.core_diameter}</p>
            )}
            <p className="text-white/30 text-xs mt-1">
              Используйте точку или запятую как разделитель
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-white/70 mb-1">
              Общий диаметр (мм)
            </label>
            <input
              type="text"
              name="total_diameter"
              value={form.total_diameter}
              onChange={handleInputChange}
              placeholder="Например: 2.9 или 2,9"
              className={`glass-input w-full ${errors.total_diameter ? 'border-red-500/50' : ''}`}
            />
            {errors.total_diameter && (
              <p className="text-red-400 text-xs mt-1">{errors.total_diameter}</p>
            )}
            <p className="text-white/30 text-xs mt-1">
              Используйте точку или запятую как разделитель
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-white/70 mb-1">
              Длина струны (мм)
            </label>
            <input
              type="text"
              name="string_length"
              value={form.string_length}
              onChange={handleInputChange}
              placeholder="Например: 1800.5 или 1800,5"
              className={`glass-input w-full ${errors.string_length ? 'border-red-500/50' : ''}`}
            />
            {errors.string_length && (
              <p className="text-red-400 text-xs mt-1">{errors.string_length}</p>
            )}
            <p className="text-white/30 text-xs mt-1">
              Используйте точку или запятую как разделитель
            </p>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full glass-btn glass-btn-primary py-3 text-lg disabled:opacity-50"
          >
            {loading ? '⏳ Расчет...' : '🧮 Рассчитать'}
          </button>
        </form>

        {result && (
          <div className="mt-8 glass p-6 rounded-2xl animate-fadeIn">
            <h3 className="text-xl font-bold text-white mb-4 text-center">
              📊 Результат расчета
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {result.copper_diameter !== undefined && (
                <>
                  <div className="glass-card p-4 text-center">
                    <div className="text-sm text-white/50">Диаметр меди</div>
                    <div className="text-2xl font-bold text-orange-300">
                      {result.copper_diameter.toFixed(2)} <span className="text-sm text-white/40">мм</span>
                    </div>
                  </div>
                  <div className="glass-card p-4 text-center">
                    <div className="text-sm text-white/50">Длина меди</div>
                    <div className="text-2xl font-bold text-green-300">
                      {result.copper_length.toFixed(2)} <span className="text-sm text-white/40">мм</span>
                    </div>
                  </div>
                </>
              )}

              {result.primary_copper_diameter !== undefined && (
                <>
                  <div className="glass-card p-4 text-center">
                    <div className="text-sm text-white/50">Диаметр первичной меди</div>
                    <div className="text-xl font-bold text-orange-300">
                      {result.primary_copper_diameter.toFixed(2)} мм
                    </div>
                  </div>
                  <div className="glass-card p-4 text-center">
                    <div className="text-sm text-white/50">Диаметр вторичной меди</div>
                    <div className="text-xl font-bold text-purple-300">
                      {result.secondary_copper_diameter.toFixed(2)} мм
                    </div>
                  </div>
                  <div className="glass-card p-4 text-center">
                    <div className="text-sm text-white/50">Длина первичной меди</div>
                    <div className="text-xl font-bold text-green-300">
                      {result.primary_copper_length.toFixed(2)} мм
                    </div>
                  </div>
                  <div className="glass-card p-4 text-center">
                    <div className="text-sm text-white/50">Длина вторичной меди</div>
                    <div className="text-xl font-bold text-green-300">
                      {result.secondary_copper_length.toFixed(2)} мм
                    </div>
                  </div>
                </>
              )}
            </div>

            {result.weight_estimate && (
              <div className="mt-4 glass p-4 rounded-xl text-center border border-amber-500/20">
                <span className="font-semibold text-white/70">⚖️ Вес меди:</span>
                <span className="ml-2 text-2xl font-bold text-amber-300">
                  {result.weight_estimate.toFixed(2)} г
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