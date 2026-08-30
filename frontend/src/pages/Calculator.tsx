import React, { useState } from 'react';
import api from '../services/api';

const Calculator: React.FC = () => {
  const [form, setForm] = useState({
    winding_type: 'single',
    core_diameter: '1.2',
    total_diameter: '1.8',
    winding_length: '1500',
    ratio: '2.5',
    end_allowance: '60',
  });
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  const parseNumber = (value: string): number => {
    const normalized = value.replace(',', '.');
    const parsed = parseFloat(normalized);
    return isNaN(parsed) ? 0 : parsed;
  };

  const validateField = (name: string, value: string): string => {
    if (value.trim() === '') return 'Поле обязательно для заполнения';
    const num = parseNumber(value);
    if (isNaN(num) || num <= 0) return 'Введите положительное число';
    return '';
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
    setErrors({ ...errors, [name]: validateField(name, value) });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const fieldsToValidate = form.winding_type === 'double'
      ? ['core_diameter', 'total_diameter', 'winding_length', 'ratio', 'end_allowance']
      : ['core_diameter', 'total_diameter', 'winding_length', 'end_allowance'];

    const newErrors: { [key: string]: string } = {};
    let hasError = false;

    fieldsToValidate.forEach((field) => {
      const val = form[field as keyof typeof form] as string;
      const err = validateField(field, val);
      if (err) { newErrors[field] = err; hasError = true; }
    });

    if (hasError) { setErrors(newErrors); return; }

    const payload: any = {
      winding_type: form.winding_type,
      core_diameter: parseNumber(form.core_diameter),
      total_diameter: parseNumber(form.total_diameter),
      winding_length: parseNumber(form.winding_length),
      end_allowance: parseNumber(form.end_allowance),
    };
    if (form.winding_type === 'double') payload.ratio = parseNumber(form.ratio);

    setLoading(true);
    try {
      const response = await api.post('/calculator/calculate', payload);
      setResult(response.data.result || response.data);
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Ошибка при расчёте');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="glass-card p-4 md:p-8">
        {/* Заголовок */}
        <div className="text-center mb-6 md:mb-8">
          <div className="text-4xl md:text-5xl mb-3">🧮</div>
          <h2 className="text-2xl md:text-3xl font-bold text-white">
            Калькулятор басовых струн
          </h2>
          <p className="text-white/50 mt-1 text-sm md:text-base">
            Расчёт меди по измерениям старой струны
          </p>
        </div>

        {/* Форма */}
        <form onSubmit={handleSubmit} className="space-y-4 md:space-y-5 max-w-lg mx-auto">
          <div>
            <label className="block text-sm font-medium text-white/70 mb-1">Тип навивки</label>
            <select
              name="winding_type"
              value={form.winding_type}
              onChange={handleInputChange}
              className="glass-select w-full"
            >
              <option value="single">Одиночная</option>
              <option value="double">Двойная</option>
            </select>
          </div>

          {form.winding_type === 'double' && (
            <div>
              <label className="block text-sm font-medium text-white/70 mb-1">
                Соотношение проволок (верхняя / нижняя)
              </label>
              <div className="flex gap-2">
                <select
                  value={['2', '2.5', '3'].includes(form.ratio) ? form.ratio : 'custom'}
                  onChange={(e) => {
                    if (e.target.value !== 'custom') {
                      setForm({ ...form, ratio: e.target.value });
                      setErrors({ ...errors, ratio: '' });
                    } else {
                      setForm({ ...form, ratio: '' });
                    }
                  }}
                  className="glass-select flex-1"
                >
                  <option value="2">1 : 2</option>
                  <option value="2.5">1 : 2,5</option>
                  <option value="3">1 : 3</option>
                  <option value="custom">Своё значение...</option>
                </select>
                {!['2', '2.5', '3'].includes(form.ratio) && (
                  <input
                    type="text"
                    name="ratio"
                    value={form.ratio}
                    onChange={handleInputChange}
                    placeholder="Например: 2.7"
                    className={`glass-input flex-1 ${errors.ratio ? 'border-red-500/50' : ''}`}
                  />
                )}
              </div>
              {errors.ratio && <p className="text-red-400 text-xs mt-1">{errors.ratio}</p>}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-white/70 mb-1">Диаметр керна (мм)</label>
            <input
              type="text" name="core_diameter" value={form.core_diameter} onChange={handleInputChange}
              placeholder="Например: 0.95"
              className={`glass-input w-full ${errors.core_diameter ? 'border-red-500/50' : ''}`}
            />
            {errors.core_diameter && <p className="text-red-400 text-xs mt-1">{errors.core_diameter}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-white/70 mb-1">Общий диаметр (мм)</label>
            <input
              type="text" name="total_diameter" value={form.total_diameter} onChange={handleInputChange}
              placeholder="Например: 4.3"
              className={`glass-input w-full ${errors.total_diameter ? 'border-red-500/50' : ''}`}
            />
            {errors.total_diameter && <p className="text-red-400 text-xs mt-1">{errors.total_diameter}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-white/70 mb-1">Длина обмотанной части (мм)</label>
            <input
              type="text" name="winding_length" value={form.winding_length} onChange={handleInputChange}
              placeholder="Например: 1500"
              className={`glass-input w-full ${errors.winding_length ? 'border-red-500/50' : ''}`}
            />
            {errors.winding_length && <p className="text-red-400 text-xs mt-1">{errors.winding_length}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-white/70 mb-1">Припуск на концы (мм)</label>
            <input
              type="text" name="end_allowance" value={form.end_allowance} onChange={handleInputChange}
              placeholder="По умолчанию: 60"
              className={`glass-input w-full ${errors.end_allowance ? 'border-red-500/50' : ''}`}
            />
            {errors.end_allowance && <p className="text-red-400 text-xs mt-1">{errors.end_allowance}</p>}
          </div>

          <button
            type="submit" disabled={loading}
            className="w-full glass-btn glass-btn-primary py-3 text-lg disabled:opacity-50 transition-all"
          >
            {loading ? '⏳ Расчёт...' : '🧮 Рассчитать'}
          </button>
        </form>

        {/* Результат текущего расчёта */}
        {result && (
          <div className="mt-6 md:mt-8 glass p-4 md:p-6 rounded-2xl animate-fadeIn border border-white/10">
            <h3 className="text-lg md:text-xl font-bold text-white mb-4 text-center text-shadow-strong">
              📊 Результат расчёта
            </h3>

            {/* Одиночная навивка */}
            {result.copper_diameter !== undefined && (
              <div className="grid grid-cols-2 gap-3 md:gap-4">
                <div className="glass-card p-4 text-center">
                  <div className="text-xs md:text-sm text-white/70 text-shadow-strong">Диаметр меди</div>
                  <div className="text-xl md:text-2xl font-bold glow-orange">
                    {result.copper_diameter.toFixed(2)} <span className="text-sm text-white/60">мм</span>
                  </div>
                </div>
                <div className="glass-card p-4 text-center">
                  <div className="text-xs md:text-sm text-white/70 text-shadow-strong">Число витков</div>
                  <div className="text-xl md:text-2xl font-bold glow-cyan">{result.turns}</div>
                </div>
                <div className="glass-card p-4 text-center">
                  <div className="text-xs md:text-sm text-white/70 text-shadow-strong">Длина меди</div>
                  <div className="text-xl md:text-2xl font-bold glow-emerald">
                    {result.copper_length_m.toFixed(2)} <span className="text-sm text-white/60">м</span>
                  </div>
                </div>
                <div className="glass-card p-4 text-center">
                  <div className="text-xs md:text-sm text-white/70 text-shadow-strong">Вес меди</div>
                  <div className="text-xl md:text-2xl font-bold glow-yellow">
                    {result.weight_g.toFixed(1)} <span className="text-sm text-white/60">г</span>
                  </div>
                </div>
              </div>
            )}

            {/* Двойная навивка */}
            {result.primary_copper_diameter !== undefined && (
              <>
                {result.ratio !== undefined && (
                  <div className="text-center text-white/70 text-sm mb-3 text-shadow-strong">
                    Соотношение 1 : {result.ratio}
                  </div>
                )}
                <div className="grid grid-cols-2 gap-3 md:gap-4 mb-3 md:mb-4">
                  <div className="glass-card p-4 text-center">
                    <div className="text-xs md:text-sm text-white/70 text-shadow-strong">Первичка ⌀</div>
                    <div className="text-lg md:text-xl font-bold glow-orange">
                      {result.primary_copper_diameter.toFixed(2)} <span className="text-sm text-white/60">мм</span>
                    </div>
                  </div>
                  <div className="glass-card p-4 text-center">
                    <div className="text-xs md:text-sm text-white/70 text-shadow-strong">Вторичка ⌀</div>
                    <div className="text-lg md:text-xl font-bold glow-fuchsia">
                      {result.secondary_copper_diameter.toFixed(2)} <span className="text-sm text-white/60">мм</span>
                    </div>
                  </div>
                  <div className="glass-card p-4 text-center">
                    <div className="text-xs md:text-sm text-white/70 text-shadow-strong">Витков первички</div>
                    <div className="text-lg md:text-xl font-bold glow-cyan">{result.primary_turns}</div>
                  </div>
                  <div className="glass-card p-4 text-center">
                    <div className="text-xs md:text-sm text-white/70 text-shadow-strong">Витков вторички</div>
                    <div className="text-lg md:text-xl font-bold glow-cyan">{result.secondary_turns}</div>
                  </div>
                  <div className="glass-card p-4 text-center">
                    <div className="text-xs md:text-sm text-white/70 text-shadow-strong">Длина первички</div>
                    <div className="text-lg md:text-xl font-bold glow-emerald">
                      {result.primary_copper_length_m.toFixed(2)} <span className="text-sm text-white/60">м</span>
                    </div>
                  </div>
                  <div className="glass-card p-4 text-center">
                    <div className="text-xs md:text-sm text-white/70 text-shadow-strong">Длина вторички</div>
                    <div className="text-lg md:text-xl font-bold glow-emerald">
                      {result.secondary_copper_length_m.toFixed(2)} <span className="text-sm text-white/60">м</span>
                    </div>
                  </div>
                  <div className="glass-card p-4 text-center">
                    <div className="text-xs md:text-sm text-white/70 text-shadow-strong">Вес первички</div>
                    <div className="text-lg md:text-xl font-bold glow-yellow">
                      {result.primary_weight_g.toFixed(1)} <span className="text-sm text-white/60">г</span>
                    </div>
                  </div>
                  <div className="glass-card p-4 text-center">
                    <div className="text-xs md:text-sm text-white/70 text-shadow-strong">Вес вторички</div>
                    <div className="text-lg md:text-xl font-bold glow-yellow">
                      {result.secondary_weight_g.toFixed(1)} <span className="text-sm text-white/60">г</span>
                    </div>
                  </div>
                </div>
                <div className="glass p-4 rounded-xl text-center border border-yellow-500/30 bg-yellow-500/5">
                  <span className="font-semibold text-white/90 text-shadow-strong">⚖️ Общий вес меди:</span>
                  <span className="ml-2 text-xl md:text-2xl font-bold glow-yellow">
                    {result.weight_g.toFixed(1)} г
                  </span>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Calculator;