import React, {useState, useEffect} from 'react';
import api from '../services/api';
import {useAuth} from '../contexts/AuthContext';

interface StringData {
    id: number;
    brand: string;
    model: string;
    chor_nummer: number;
    saiten_im_chor: number | null;
    laenge_mm: number | null;
    kern_mm: number;
    erste_wicklung_mm: number | null;
    zweite_wicklung_mm: number | null;
    typ: string | null;
    year: string | null;
}

const Strings: React.FC = () => {
    const {user} = useAuth();
    const [brands, setBrands] = useState<{ brand: string }[]>([]);
    const [models, setModels] = useState<{ model: string }[]>([]);
    const [choruses, setChoruses] = useState<{ chor_nummer: number }[]>([]);
    const [data, setData] = useState<StringData[]>([]);
    const [loading, setLoading] = useState(false);
    const [selectedBrand, setSelectedBrand] = useState('');
    const [selectedModel, setSelectedModel] = useState('');
    const [selectedChorus, setSelectedChorus] = useState<number | ''>('');
    const [showAddForm, setShowAddForm] = useState(false);
    const [editingId, setEditingId] = useState<number | null>(null);

    const isAdmin = user?.is_admin || user?.is_super_admin;

    const [newRecord, setNewRecord] = useState({
        brand: '',
        model: '',
        chor_nummer: 0,
        saiten_im_chor: '',
        laenge_mm: '',
        kern_mm: 0,
        erste_wicklung_mm: '',
        zweite_wicklung_mm: '',
        typ: '',
        year: ''
    });

    useEffect(() => {
        loadBrands();
    }, []);

    const loadBrands = async () => {
        try {
            const response = await api.get('/strings/brands');
            setBrands(response.data);
        } catch (error) {
            console.error('Ошибка загрузки брендов:', error);
        }
    };

    const loadModels = async (brand: string) => {
        try {
            const response = await api.get(`/strings/models/${brand}`);
            setModels(response.data);
            setSelectedModel('');
            setChoruses([]);
            setData([]);
        } catch (error) {
            console.error('Ошибка загрузки моделей:', error);
        }
    };

    const loadChoruses = async (brand: string, model: string) => {
        try {
            const encodedModel = encodeURIComponent(model);
            const response = await api.get(`/strings/choruses/${brand}/${encodedModel}`);
            setChoruses(response.data);
            setSelectedChorus('');
            setData([]);
        } catch (error) {
            console.error('Ошибка загрузки хоров:', error);
        }
    };

    const loadData = async (brand: string, model: string, chorus: number) => {
        setLoading(true);
        try {
            const encodedModel = encodeURIComponent(model);
            const response = await api.get(`/strings/data/${brand}/${encodedModel}/${chorus}`);
            setData(response.data);
        } catch (error) {
            console.error('Ошибка загрузки данных:', error);
            setData([]);
        } finally {
            setLoading(false);
        }
    };

    const handleBrandChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const brand = e.target.value;
        setSelectedBrand(brand);
        if (brand) {
            loadModels(brand);
        } else {
            setModels([]);
            setChoruses([]);
            setData([]);
        }
    };

    const handleModelChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const model = e.target.value;
        setSelectedModel(model);
        if (model) {
            loadChoruses(selectedBrand, model);
        } else {
            setChoruses([]);
            setData([]);
        }
    };

    const handleChorusChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const chorus = parseInt(e.target.value);
        setSelectedChorus(chorus);
        if (chorus) {
            loadData(selectedBrand, selectedModel, chorus);
        } else {
            setData([]);
        }
    };

    const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await api.post('/strings/import-csv', formData, {
                headers: {'Content-Type': 'multipart/form-data'}
            });
            alert(`✅ Добавлено: ${response.data.added}\n❌ Ошибок: ${response.data.errors?.length || 0}`);
            if (selectedBrand && selectedModel && selectedChorus) {
                loadData(selectedBrand, selectedModel, selectedChorus as number);
            }
        } catch (error: any) {
            alert('❌ Ошибка импорта: ' + (error.response?.data?.detail || 'Неизвестная ошибка'));
        }
        e.target.value = '';
    };

    const handleAdd = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await api.post('/strings/data', {
                brand: newRecord.brand,
                model: newRecord.model,
                chor_nummer: newRecord.chor_nummer,
                saiten_im_chor: newRecord.saiten_im_chor ? parseInt(newRecord.saiten_im_chor) : null,
                laenge_mm: newRecord.laenge_mm ? parseFloat(newRecord.laenge_mm) : null,
                kern_mm: newRecord.kern_mm,
                erste_wicklung_mm: newRecord.erste_wicklung_mm ? parseFloat(newRecord.erste_wicklung_mm) : null,
                zweite_wicklung_mm: newRecord.zweite_wicklung_mm ? parseFloat(newRecord.zweite_wicklung_mm) : null,
                typ: newRecord.typ || null,
                year: newRecord.year || null
            });
            alert('✅ Запись добавлена');
            setShowAddForm(false);
            setNewRecord({
                brand: '',
                model: '',
                chor_nummer: 0,
                saiten_im_chor: '',
                laenge_mm: '',
                kern_mm: 0,
                erste_wicklung_mm: '',
                zweite_wicklung_mm: '',
                typ: '',
                year: ''
            });
            if (selectedBrand && selectedModel && selectedChorus) {
                loadData(selectedBrand, selectedModel, selectedChorus as number);
            }
        } catch (error) {
            alert('❌ Ошибка добавления');
        }
    };

    const handleDelete = async (id: number) => {
        if (!window.confirm('Удалить запись?')) return;
        try {
            await api.delete(`/strings/data/${id}`);
            alert('✅ Запись удалена');
            if (selectedBrand && selectedModel && selectedChorus) {
                loadData(selectedBrand, selectedModel, selectedChorus as number);
            }
        } catch (error) {
            alert('❌ Ошибка удаления');
        }
    };

    const handleEdit = (record: StringData) => {
        setEditingId(record.id);
        setNewRecord({
            brand: record.brand,
            model: record.model,
            chor_nummer: record.chor_nummer,
            saiten_im_chor: record.saiten_im_chor?.toString() || '',
            laenge_mm: record.laenge_mm?.toString() || '',
            kern_mm: record.kern_mm,
            erste_wicklung_mm: record.erste_wicklung_mm?.toString() || '',
            zweite_wicklung_mm: record.zweite_wicklung_mm?.toString() || '',
            typ: record.typ || '',
            year: record.year || ''
        });
        setShowAddForm(true);
    };

    const handleUpdate = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!editingId) return;
        try {
            await api.put(`/strings/data/${editingId}`, {
                brand: newRecord.brand,
                model: newRecord.model,
                chor_nummer: newRecord.chor_nummer,
                saiten_im_chor: newRecord.saiten_im_chor ? parseInt(newRecord.saiten_im_chor) : null,
                laenge_mm: newRecord.laenge_mm ? parseFloat(newRecord.laenge_mm) : null,
                kern_mm: newRecord.kern_mm,
                erste_wicklung_mm: newRecord.erste_wicklung_mm ? parseFloat(newRecord.erste_wicklung_mm) : null,
                zweite_wicklung_mm: newRecord.zweite_wicklung_mm ? parseFloat(newRecord.zweite_wicklung_mm) : null,
                typ: newRecord.typ || null,
                year: newRecord.year || null
            });
            alert('✅ Запись обновлена');
            setShowAddForm(false);
            setEditingId(null);
            setNewRecord({
                brand: '',
                model: '',
                chor_nummer: 0,
                saiten_im_chor: '',
                laenge_mm: '',
                kern_mm: 0,
                erste_wicklung_mm: '',
                zweite_wicklung_mm: '',
                typ: '',
                year: ''
            });
            if (selectedBrand && selectedModel && selectedChorus) {
                loadData(selectedBrand, selectedModel, selectedChorus as number);
            }
        } catch (error) {
            alert('❌ Ошибка обновления');
        }
    };

    return (
        <div className="max-w-7xl mx-auto">
            <div className="glass-card p-8">
                <div className="text-center mb-8">
                    <div className="text-5xl mb-3">🎵</div>
                    <h2 className="text-3xl font-bold text-white">Мензуры струн</h2>
                    <p className="text-white/50 mt-1">Данные по длинам и диаметрам струн</p>
                </div>

                <div className="flex flex-wrap gap-4 mb-6">
                    <select
                        value={selectedBrand}
                        onChange={handleBrandChange}
                        className="glass-input flex-1 min-w-[150px]"
                    >
                        <option value="">Выберите бренд</option>
                        {brands.map((b) => (
                            <option key={b.brand} value={b.brand}>{b.brand}</option>
                        ))}
                    </select>

                    <select
                        value={selectedModel}
                        onChange={handleModelChange}
                        className="glass-input flex-1 min-w-[150px]"
                        disabled={!selectedBrand}
                    >
                        <option value="">Выберите модель</option>
                        {models.map((m) => (
                            <option key={m.model} value={m.model}>{m.model}</option>
                        ))}
                    </select>

                    <select
                        value={selectedChorus}
                        onChange={handleChorusChange}
                        className="glass-input flex-1 min-w-[150px]"
                        disabled={!selectedModel}
                    >
                        <option value="">Выберите хор</option>
                        {choruses.map((c) => (
                            <option key={c.chor_nummer} value={c.chor_nummer}>
                                Хор {c.chor_nummer}
                            </option>
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
                                onClick={() => {
                                    setShowAddForm(!showAddForm);
                                    if (!showAddForm) {
                                        setEditingId(null);
                                        setNewRecord({
                                            brand: selectedBrand || '',
                                            model: selectedModel || '',
                                            chor_nummer: selectedChorus as number || 0,
                                            saiten_im_chor: '',
                                            laenge_mm: '',
                                            kern_mm: 0,
                                            erste_wicklung_mm: '',
                                            zweite_wicklung_mm: '',
                                            typ: '',
                                            year: ''
                                        });
                                    }
                                }}
                                className="glass-btn"
                            >
                                {showAddForm ? '❌ Отмена' : '➕ Добавить'}
                            </button>
                        </>
                    )}
                </div>

                {showAddForm && isAdmin && (
                    <form onSubmit={editingId ? handleUpdate : handleAdd} className="mb-6 glass p-6 rounded-2xl">
                        <h4 className="font-semibold text-white mb-4">
                            {editingId ? '✏️ Редактирование записи' : '➕ Добавление записи'}
                        </h4>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <input
                                type="text"
                                placeholder="Бренд *"
                                value={newRecord.brand}
                                onChange={(e) => setNewRecord({...newRecord, brand: e.target.value})}
                                className="glass-input"
                                required
                            />
                            <input
                                type="text"
                                placeholder="Модель *"
                                value={newRecord.model}
                                onChange={(e) => setNewRecord({...newRecord, model: e.target.value})}
                                className="glass-input"
                                required
                            />
                            <input
                                type="number"
                                placeholder="№ хора *"
                                value={newRecord.chor_nummer || ''}
                                onChange={(e) => setNewRecord({
                                    ...newRecord,
                                    chor_nummer: parseInt(e.target.value) || 0
                                })}
                                className="glass-input"
                                required
                            />
                            <input
                                type="number"
                                placeholder="Струн в хоре"
                                value={newRecord.saiten_im_chor}
                                onChange={(e) => setNewRecord({...newRecord, saiten_im_chor: e.target.value})}
                                className="glass-input"
                            />
                            <input
                                type="number"
                                step="0.01"
                                placeholder="Длина (мм)"
                                value={newRecord.laenge_mm}
                                onChange={(e) => setNewRecord({...newRecord, laenge_mm: e.target.value})}
                                className="glass-input"
                            />
                            <input
                                type="number"
                                step="0.01"
                                placeholder="Керн (мм) *"
                                value={newRecord.kern_mm || ''}
                                onChange={(e) => setNewRecord({...newRecord, kern_mm: parseFloat(e.target.value) || 0})}
                                className="glass-input"
                                required
                            />
                            <input
                                type="number"
                                step="0.01"
                                placeholder="1-я навивка"
                                value={newRecord.erste_wicklung_mm}
                                onChange={(e) => setNewRecord({...newRecord, erste_wicklung_mm: e.target.value})}
                                className="glass-input"
                            />
                            <input
                                type="number"
                                step="0.01"
                                placeholder="2-я навивка"
                                value={newRecord.zweite_wicklung_mm}
                                onChange={(e) => setNewRecord({...newRecord, zweite_wicklung_mm: e.target.value})}
                                className="glass-input"
                            />
                            <input
                                type="text"
                                placeholder="Тип (bass/plain)"
                                value={newRecord.typ}
                                onChange={(e) => setNewRecord({...newRecord, typ: e.target.value})}
                                className="glass-input"
                            />
                            <input
                                type="text"
                                placeholder="Год"
                                value={newRecord.year}
                                onChange={(e) => setNewRecord({...newRecord, year: e.target.value})}
                                className="glass-input"
                            />
                        </div>
                        <button
                            type="submit"
                            className="mt-4 glass-btn glass-btn-primary"
                        >
                            {editingId ? '💾 Сохранить' : '✅ Добавить'}
                        </button>
                    </form>
                )}

                {loading ? (
                    <div className="text-center py-12">
                        <div
                            className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-white border-t-transparent"></div>
                        <p className="mt-2 text-white/50">Загрузка...</p>
                    </div>
                ) : data.length === 0 ? (
                    <div className="text-center py-12">
                        <div className="text-4xl mb-2">📭</div>
                        <p className="text-white/50">Нет данных</p>
                        <p className="text-white/30 text-sm mt-1">Выберите бренд, модель и хор</p>
                    </div>
                ) : (
                    <div className="glass-table">
                        <table className="min-w-full divide-y divide-white/5 text-sm">
                            <thead>
                            <tr>
                                <th className="px-4 py-3 text-left font-medium text-white/40">№</th>
                                <th className="px-4 py-3 text-left font-medium text-white/40">Бренд</th>
                                <th className="px-4 py-3 text-left font-medium text-white/40">Модель</th>
                                <th className="px-4 py-3 text-left font-medium text-white/40">Хор</th>
                                <th className="px-4 py-3 text-left font-medium text-white/40">Струн в хоре</th>
                                <th className="px-4 py-3 text-left font-medium text-white/40">Длина (мм)</th>
                                <th className="px-4 py-3 text-left font-medium text-white/40">Керн (мм)</th>
                                <th className="px-4 py-3 text-left font-medium text-white/40">Первичная навивка</th>
                                <th className="px-4 py-3 text-left font-medium text-white/40">Вторичная навивка</th>
                                <th className="px-4 py-3 text-left font-medium text-white/40">Тип</th>
                                <th className="px-4 py-3 text-left font-medium text-white/40">Год</th>
                                {isAdmin && <th className="px-4 py-3 text-left font-medium text-white/40">Действия</th>}
                            </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                            {data.map((row) => (
                                <tr key={row.id} className="hover:bg-white/5 transition">
                                    <td className="px-4 py-3 text-white/60">{row.id}</td>
                                    <td className="px-4 py-3 font-medium text-white">{row.brand}</td>
                                    <td className="px-4 py-3 text-white/80">{row.model}</td>
                                    <td className="px-4 py-3 text-white/80">{row.chor_nummer}</td>
                                    <td className="px-4 py-3 text-white/80">{row.saiten_im_chor || '—'}</td>
                                    <td className="px-4 py-3 text-white/80">{row.laenge_mm || '—'}</td>
                                    <td className="px-4 py-3 font-semibold text-indigo-300">{row.kern_mm}</td>
                                    <td className="px-4 py-3 text-white/80">{row.erste_wicklung_mm || '—'}</td>
                                    <td className="px-4 py-3 text-white/80">
                                        {row.zweite_wicklung_mm !== null && row.zweite_wicklung_mm !== undefined && row.zweite_wicklung_mm > 0
                                            ? row.zweite_wicklung_mm
                                            : '—'}
                                    </td>
                                    <td className="px-4 py-3 text-white/80">{row.typ || '—'}</td>
                                    <td className="px-4 py-3 text-white/80">{row.year || '—'}</td>
                                    {isAdmin && (
                                        <td className="px-4 py-3 space-x-2">
                                            <button
                                                onClick={() => handleEdit(row)}
                                                className="text-blue-400 hover:text-blue-300 transition font-medium"
                                            >
                                                ✏️
                                            </button>
                                            <button
                                                onClick={() => handleDelete(row.id)}
                                                className="text-red-400 hover:text-red-300 transition font-medium"
                                            >
                                                🗑️
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

export default Strings;