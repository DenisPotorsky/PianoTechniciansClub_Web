import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';

interface User {
  id: number;
  telegram_id: number;
  username: string;
  first_name: string;
  last_name: string | null;
  is_subscribed: boolean;
  is_admin: boolean;
  is_super_admin: boolean;
  created_at: string;
}

interface Brand {
  id: number;
  name: string;
  country: string;
  type: string;
  info: string | null;
  ranges_count: number;
}

interface AccessRequest {
  id: number;
  user_id: number;
  username: string;
  full_name: string;
  message: string | null;
  status: string;
  created_at: string;
}

const Admin: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'stats' | 'users' | 'whitelist' | 'requests' | 'brands'>('stats');
  const [stats, setStats] = useState<any>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [whitelist, setWhitelist] = useState<any[]>([]);
  const [requests, setRequests] = useState<AccessRequest[]>([]);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);

  // Редактирование пользователя
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editForm, setEditForm] = useState({
    first_name: '',
    last_name: '',
    username: '',
    is_subscribed: false,
    is_admin: false,
    new_password: ''
  });

  const [newBrand, setNewBrand] = useState({
    name: '',
    country: '',
    type: 'foreign',
    info: '',
    ranges: [{ serial_start: 1, serial_end: 1000, year: 1900 }]
  });

  const [newAdminId, setNewAdminId] = useState('');

  useEffect(() => {
    loadStats();
    loadUsers();
    loadWhitelist();
    loadRequests();
    loadBrands();
  }, []);

  const loadStats = async () => {
    try {
      const response = await api.get('/admin/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Ошибка загрузки статистики:', error);
    }
  };

  const loadUsers = async () => {
    try {
      const response = await api.get('/admin/users');
      setUsers(response.data);
    } catch (error) {
      console.error('Ошибка загрузки пользователей:', error);
    }
  };

  const loadWhitelist = async () => {
    try {
      const response = await api.get('/admin/whitelist');
      setWhitelist(response.data);
    } catch (error) {
      console.error('Ошибка загрузки белого списка:', error);
    }
  };

  const loadRequests = async () => {
    try {
      const response = await api.get('/admin/requests');
      setRequests(response.data);
    } catch (error) {
      console.error('Ошибка загрузки заявок:', error);
    }
  };

  const loadBrands = async () => {
    try {
      const response = await api.get('/admin/brands');
      setBrands(response.data);
    } catch (error) {
      console.error('Ошибка загрузки брендов:', error);
    }
  };

  const handleAddAdmin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newAdminId) return;
    setLoading(true);
    try {
      await api.post(`/admin/whitelist/add?telegram_id=${parseInt(newAdminId)}`);
      alert('✅ Пользователь добавлен в белый список');
      setNewAdminId('');
      loadWhitelist();
      loadUsers();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Ошибка');
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveAdmin = async (telegramId: number) => {
    if (!window.confirm('Удалить пользователя из белого списка?')) return;
    try {
      await api.post(`/admin/whitelist/remove?telegram_id=${telegramId}`);
      alert('✅ Пользователь удалён из белого списка');
      loadWhitelist();
      loadUsers();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Ошибка');
    }
  };

  const handleProcessRequest = async (requestId: number, action: 'approve' | 'reject') => {
    try {
      await api.post(`/admin/requests/${requestId}/${action}`);
      alert(action === 'approve' ? '✅ Заявка одобрена' : '❌ Заявка отклонена');
      loadRequests();
      loadUsers();
      loadStats();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Ошибка');
    }
  };

  const handleDeleteUser = async (userId: number) => {
    if (!window.confirm('Удалить пользователя?')) return;
    try {
      await api.delete(`/admin/users/${userId}`);
      alert('✅ Пользователь удалён');
      loadUsers();
      loadStats();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Ошибка');
    }
  };

  const handleEditUser = (user: User) => {
    setEditingUser(user);
    setEditForm({
      first_name: user.first_name,
      last_name: user.last_name || '',
      username: user.username || '',
      is_subscribed: user.is_subscribed,
      is_admin: user.is_admin,
      new_password: ''
    });
    setShowEditModal(true);
  };

  const handleSaveUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingUser) return;
    setLoading(true);
    try {
      await api.put(`/admin/users/${editingUser.id}`, {
        first_name: editForm.first_name,
        last_name: editForm.last_name || null,
        username: editForm.username,
        is_subscribed: editForm.is_subscribed,
        is_admin: editForm.is_admin
      });

      if (editForm.new_password) {
        await api.put(`/admin/users/${editingUser.id}/password?password=${editForm.new_password}`);
      }

      alert('✅ Пользователь обновлён');
      setShowEditModal(false);
      setEditingUser(null);
      loadUsers();
      loadWhitelist();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Ошибка при обновлении');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteBrand = async (brandId: number) => {
    if (!window.confirm('Удалить бренд?')) return;
    try {
      await api.delete(`/admin/brands/${brandId}`);
      alert('✅ Бренд удалён');
      loadBrands();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Ошибка');
    }
  };

  const addRange = () => {
    setNewBrand({
      ...newBrand,
      ranges: [...newBrand.ranges, { serial_start: 1, serial_end: 1000, year: 1900 }]
    });
  };

  const removeRange = (index: number) => {
    const ranges = newBrand.ranges.filter((_, i) => i !== index);
    setNewBrand({ ...newBrand, ranges });
  };

  const updateRange = (index: number, field: string, value: string) => {
    const ranges = newBrand.ranges.map((r, i) =>
      i === index ? { ...r, [field]: parseInt(value) || 0 } : r
    );
    setNewBrand({ ...newBrand, ranges });
  };

  const handleAddBrand = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post('/admin/brands', {
        name: newBrand.name,
        country: newBrand.country,
        type: newBrand.type,
        info: newBrand.info || null
      });

      const response = await api.get('/admin/brands');
      const createdBrand = response.data.find((b: any) => b.name === newBrand.name);

      if (createdBrand) {
        for (const range of newBrand.ranges) {
          await api.post(`/admin/brands/${createdBrand.id}/ranges`, range);
        }
      }

      alert('✅ Бренд добавлен!');
      setShowAddForm(false);
      setNewBrand({
        name: '',
        country: '',
        type: 'foreign',
        info: '',
        ranges: [{ serial_start: 1, serial_end: 1000, year: 1900 }]
      });
      loadBrands();
    } catch (error: any) {
      console.error('Ошибка:', error);
      alert(error.response?.data?.detail || 'Ошибка при добавлении');
    } finally {
      setLoading(false);
    }
  };

  const filteredUsers = users.filter(u =>
    u.username?.toLowerCase().includes(search.toLowerCase()) ||
    u.first_name?.toLowerCase().includes(search.toLowerCase()) ||
    String(u.telegram_id).includes(search)
  );

  return (
    <div className="max-w-7xl mx-auto">
      <div className="bg-white rounded-3xl shadow-2xl p-8 border border-gray-100">
        <div className="text-center mb-8">
          <div className="text-4xl mb-2">👑</div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-700 to-indigo-700 bg-clip-text text-transparent">
            Админ-панель
          </h2>
          <p className="text-gray-500 mt-1">Управление клубом</p>
        </div>

        {/* Вкладки */}
        <div className="flex flex-wrap gap-2 mb-6 border-b border-gray-200 pb-2">
          <button
            onClick={() => setActiveTab('stats')}
            className={`px-5 py-2.5 rounded-xl font-medium transition-all ${
              activeTab === 'stats' 
                ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md' 
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            📊 Статистика
          </button>
          <button
            onClick={() => setActiveTab('users')}
            className={`px-5 py-2.5 rounded-xl font-medium transition-all ${
              activeTab === 'users' 
                ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md' 
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            👥 Пользователи
          </button>
          <button
            onClick={() => setActiveTab('whitelist')}
            className={`px-5 py-2.5 rounded-xl font-medium transition-all ${
              activeTab === 'whitelist' 
                ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md' 
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            🔓 Белый список
          </button>
          <button
            onClick={() => setActiveTab('requests')}
            className={`px-5 py-2.5 rounded-xl font-medium transition-all ${
              activeTab === 'requests' 
                ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md' 
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            📩 Заявки {stats?.pending_requests > 0 && `(${stats.pending_requests})`}
          </button>
          <button
            onClick={() => setActiveTab('brands')}
            className={`px-5 py-2.5 rounded-xl font-medium transition-all ${
              activeTab === 'brands' 
                ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md' 
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            📖 Атлас
          </button>
        </div>

        {/* Статистика */}
        {activeTab === 'stats' && stats && (
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-5 rounded-2xl text-center border border-blue-100 shadow-sm hover:shadow-md transition">
              <div className="text-2xl font-bold text-blue-700">{stats.total_users}</div>
              <div className="text-sm text-gray-600 mt-1">Всего пользователей</div>
            </div>
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 p-5 rounded-2xl text-center border border-green-100 shadow-sm hover:shadow-md transition">
              <div className="text-2xl font-bold text-green-700">{stats.subscribed_users}</div>
              <div className="text-sm text-gray-600 mt-1">Подписаны</div>
            </div>
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 p-5 rounded-2xl text-center border border-purple-100 shadow-sm hover:shadow-md transition">
              <div className="text-2xl font-bold text-purple-700">{stats.admin_users}</div>
              <div className="text-sm text-gray-600 mt-1">Админы</div>
            </div>
            <div className="bg-gradient-to-br from-orange-50 to-amber-50 p-5 rounded-2xl text-center border border-orange-100 shadow-sm hover:shadow-md transition">
              <div className="text-2xl font-bold text-orange-700">{stats.total_calculations}</div>
              <div className="text-sm text-gray-600 mt-1">Расчётов</div>
            </div>
            <div className="bg-gradient-to-br from-yellow-50 to-amber-50 p-5 rounded-2xl text-center border border-yellow-100 shadow-sm hover:shadow-md transition">
              <div className="text-2xl font-bold text-yellow-700">{stats.pending_requests}</div>
              <div className="text-sm text-gray-600 mt-1">Заявок</div>
            </div>
          </div>
        )}

        {/* Пользователи */}
        {activeTab === 'users' && (
          <div>
            <div className="flex justify-between items-center mb-4 flex-wrap gap-2">
              <h3 className="text-xl font-semibold text-gray-800">👥 Пользователи</h3>
              <input
                type="text"
                placeholder="🔍 Поиск..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="px-4 py-2 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-4 focus:ring-indigo-200 transition-all outline-none"
              />
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left font-medium text-gray-500">ID</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-500">Имя</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-500">Telegram ID</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-500">Статус</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-500">Роль</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-500">Действия</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {filteredUsers.map((u) => (
                    <tr key={u.id} className="hover:bg-gray-50 transition">
                      <td className="px-4 py-3">{u.id}</td>
                      <td className="px-4 py-3 font-medium">{u.first_name} {u.last_name}</td>
                      <td className="px-4 py-3">{u.telegram_id}</td>
                      <td className="px-4 py-3">
                        {u.is_subscribed ?
                          <span className="px-2.5 py-1 bg-green-100 text-green-700 rounded-full text-xs font-semibold">✅ Подписан</span> :
                          <span className="px-2.5 py-1 bg-gray-100 text-gray-500 rounded-full text-xs font-semibold">⏳ Ожидает</span>
                        }
                      </td>
                      <td className="px-4 py-3">
                        {u.is_super_admin ? '👑 Супер-админ' : u.is_admin ? '⭐ Админ' : '👤 Пользователь'}
                      </td>
                      <td className="px-4 py-3 space-x-2">
                        {!u.is_super_admin && (
                          <>
                            <button
                              onClick={() => handleEditUser(u)}
                              className="text-blue-600 hover:text-blue-800 transition font-medium"
                            >
                              ✏️ Редактировать
                            </button>
                            <button
                              onClick={() => handleDeleteUser(u.id)}
                              className="text-red-600 hover:text-red-800 transition font-medium"
                            >
                              🗑️ Удалить
                            </button>
                          </>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Белый список */}
        {activeTab === 'whitelist' && (
          <div>
            <div className="flex justify-between items-center mb-4 flex-wrap gap-2">
              <h3 className="text-xl font-semibold text-gray-800">🔓 Белый список (Администраторы)</h3>
            </div>

            {user?.is_super_admin && (
              <form onSubmit={handleAddAdmin} className="mb-4 flex gap-2 flex-wrap">
                <input
                  type="number"
                  placeholder="Telegram ID пользователя"
                  value={newAdminId}
                  onChange={(e) => setNewAdminId(e.target.value)}
                  className="px-4 py-2 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-4 focus:ring-indigo-200 transition-all outline-none"
                  required
                />
                <button
                  type="submit"
                  disabled={loading}
                  className="px-6 py-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-semibold rounded-xl shadow-md hover:shadow-lg transition-all duration-200 disabled:opacity-50"
                >
                  ➕ Добавить админа
                </button>
              </form>
            )}

            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left font-medium text-gray-500">ID</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-500">Имя</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-500">Telegram ID</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-500">Роль</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-500">Действия</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {whitelist.map((a) => (
                    <tr key={a.id} className="hover:bg-gray-50 transition">
                      <td className="px-4 py-3">{a.id}</td>
                      <td className="px-4 py-3 font-medium">{a.first_name} {a.last_name}</td>
                      <td className="px-4 py-3">{a.telegram_id}</td>
                      <td className="px-4 py-3">
                        {a.is_super_admin ? '👑 Супер-админ' : '⭐ Админ'}
                      </td>
                      <td className="px-4 py-3">
                        {!a.is_super_admin && user?.is_super_admin && (
                          <button onClick={() => handleRemoveAdmin(a.telegram_id)} className="text-red-600 hover:text-red-800 transition font-medium">
                            🗑️ Удалить
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Заявки */}
        {activeTab === 'requests' && (
          <div>
            <h3 className="text-xl font-semibold text-gray-800 mb-4">📩 Заявки на доступ</h3>
            {requests.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <div className="text-4xl mb-2">✅</div>
                <p>Нет активных заявок</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left font-medium text-gray-500">Пользователь</th>
                      <th className="px-4 py-3 text-left font-medium text-gray-500">Сообщение</th>
                      <th className="px-4 py-3 text-left font-medium text-gray-500">Дата</th>
                      <th className="px-4 py-3 text-left font-medium text-gray-500">Действия</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {requests.map((r) => (
                      <tr key={r.id} className="hover:bg-gray-50 transition">
                        <td className="px-4 py-3 font-medium">{r.full_name} (@{r.username})</td>
                        <td className="px-4 py-3 text-gray-600">{r.message || '—'}</td>
                        <td className="px-4 py-3 text-sm">{new Date(r.created_at).toLocaleDateString()}</td>
                        <td className="px-4 py-3 space-x-2">
                          <button
                            onClick={() => handleProcessRequest(r.id, 'approve')}
                            className="px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium transition"
                          >
                            ✅ Одобрить
                          </button>
                          <button
                            onClick={() => handleProcessRequest(r.id, 'reject')}
                            className="px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-medium transition"
                          >
                            ❌ Отклонить
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Атлас */}
        {activeTab === 'brands' && (
          <div>
            <div className="flex justify-between items-center mb-4 flex-wrap gap-2">
              <h3 className="text-xl font-semibold text-gray-800">📖 Атлас</h3>
              <button
                onClick={() => setShowAddForm(!showAddForm)}
                className="px-4 py-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-semibold rounded-xl shadow-md hover:shadow-lg transition-all duration-200"
              >
                {showAddForm ? '❌ Отмена' : '➕ Добавить бренд'}
              </button>
            </div>

            {showAddForm && (
              <form onSubmit={handleAddBrand} className="mb-6 p-6 bg-gray-50 rounded-2xl border-2 border-gray-200">
                <h4 className="font-semibold text-gray-800 mb-4">➕ Добавление бренда</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <input
                    type="text"
                    placeholder="Название бренда *"
                    value={newBrand.name}
                    onChange={(e) => setNewBrand({...newBrand, name: e.target.value})}
                    className="px-4 py-2 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-4 focus:ring-indigo-200 transition-all outline-none"
                    required
                  />
                  <input
                    type="text"
                    placeholder="Страна *"
                    value={newBrand.country}
                    onChange={(e) => setNewBrand({...newBrand, country: e.target.value})}
                    className="px-4 py-2 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-4 focus:ring-indigo-200 transition-all outline-none"
                    required
                  />
                  <select
                    value={newBrand.type}
                    onChange={(e) => setNewBrand({...newBrand, type: e.target.value})}
                    className="px-4 py-2 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-4 focus:ring-indigo-200 transition-all outline-none"
                  >
                    <option value="foreign">🌍 Иностранные</option>
                    <option value="russian">🇷🇺 Отечественные</option>
                  </select>
                  <input
                    type="text"
                    placeholder="Дополнительная информация"
                    value={newBrand.info}
                    onChange={(e) => setNewBrand({...newBrand, info: e.target.value})}
                    className="px-4 py-2 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-4 focus:ring-indigo-200 transition-all outline-none"
                  />
                </div>

                <h5 className="font-medium mt-4 mb-2 text-gray-700">📊 Диапазоны серийных номеров</h5>
                {newBrand.ranges.map((range, index) => (
                  <div key={index} className="flex gap-2 items-center mb-2 flex-wrap">
                    <input
                      type="number"
                      placeholder="Начало"
                      value={range.serial_start}
                      onChange={(e) => updateRange(index, 'serial_start', e.target.value)}
                      className="w-24 px-3 py-2 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-4 focus:ring-indigo-200 transition-all outline-none"
                    />
                    <span className="text-gray-500">—</span>
                    <input
                      type="number"
                      placeholder="Конец"
                      value={range.serial_end}
                      onChange={(e) => updateRange(index, 'serial_end', e.target.value)}
                      className="w-24 px-3 py-2 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-4 focus:ring-indigo-200 transition-all outline-none"
                    />
                    <input
                      type="number"
                      placeholder="Год"
                      value={range.year}
                      onChange={(e) => updateRange(index, 'year', e.target.value)}
                      className="w-24 px-3 py-2 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-4 focus:ring-indigo-200 transition-all outline-none"
                    />
                    <button
                      type="button"
                      onClick={() => removeRange(index)}
                      className="text-red-600 hover:text-red-800 px-2 text-xl font-bold"
                    >
                      ✕
                    </button>
                  </div>
                ))}

                <button
                  type="button"
                  onClick={addRange}
                  className="mt-2 text-indigo-600 hover:text-indigo-800 text-sm font-medium"
                >
                  + Добавить диапазон
                </button>

                <div className="mt-4 flex gap-3">
                  <button
                    type="submit"
                    disabled={loading}
                    className="px-6 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold rounded-xl shadow-md hover:shadow-lg transition-all duration-200 disabled:opacity-50"
                  >
                    {loading ? 'Добавление...' : '✅ Добавить бренд'}
                  </button>
                </div>
              </form>
            )}

            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left font-medium text-gray-500">Название</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-500">Страна</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-500">Тип</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-500">Диапазонов</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-500">Действия</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {brands.map((b) => (
                    <tr key={b.id} className="hover:bg-gray-50 transition">
                      <td className="px-4 py-3 font-medium">{b.name}</td>
                      <td className="px-4 py-3">{b.country}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2.5 py-1 text-xs rounded-full font-semibold ${b.type === 'foreign' ? 'bg-blue-100 text-blue-700' : 'bg-red-100 text-red-700'}`}>
                          {b.type === 'foreign' ? '🌍 Иностранный' : '🇷🇺 Отечественный'}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center">{b.ranges_count}</td>
                      <td className="px-4 py-3">
                        <button onClick={() => handleDeleteBrand(b.id)} className="text-red-600 hover:text-red-800 transition font-medium">
                          🗑️ Удалить
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Модальное окно редактирования пользователя */}
      {showEditModal && editingUser && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-3xl shadow-2xl p-8 max-w-md w-full">
            <h3 className="text-2xl font-bold text-gray-800 mb-4">✏️ Редактирование пользователя</h3>
            <p className="text-sm text-gray-500 mb-4">Редактирование: {editingUser.username}</p>

            <form onSubmit={handleSaveUser} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Имя</label>
                <input
                  type="text"
                  value={editForm.first_name}
                  onChange={(e) => setEditForm({...editForm, first_name: e.target.value})}
                  className="mt-1 w-full px-4 py-2 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-4 focus:ring-indigo-200 transition-all outline-none"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Фамилия</label>
                <input
                  type="text"
                  value={editForm.last_name}
                  onChange={(e) => setEditForm({...editForm, last_name: e.target.value})}
                  className="mt-1 w-full px-4 py-2 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-4 focus:ring-indigo-200 transition-all outline-none"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Имя пользователя</label>
                <input
                  type="text"
                  value={editForm.username}
                  onChange={(e) => setEditForm({...editForm, username: e.target.value})}
                  className="mt-1 w-full px-4 py-2 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-4 focus:ring-indigo-200 transition-all outline-none"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Новый пароль (если нужно сбросить)</label>
                <input
                  type="text"
                  placeholder="Оставьте пустым, чтобы не менять"
                  value={editForm.new_password}
                  onChange={(e) => setEditForm({...editForm, new_password: e.target.value})}
                  className="mt-1 w-full px-4 py-2 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-4 focus:ring-indigo-200 transition-all outline-none"
                />
              </div>
              <div className="flex items-center gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={editForm.is_subscribed}
                    onChange={(e) => setEditForm({...editForm, is_subscribed: e.target.checked})}
                    className="w-4 h-4 accent-indigo-600"
                  />
                  <span className="text-sm text-gray-700">Подписан</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={editForm.is_admin}
                    onChange={(e) => setEditForm({...editForm, is_admin: e.target.checked})}
                    className="w-4 h-4 accent-indigo-600"
                    disabled={editingUser.is_super_admin}
                  />
                  <span className="text-sm text-gray-700">Администратор</span>
                </label>
              </div>
              <div className="flex gap-3 mt-4">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold rounded-xl shadow-md hover:shadow-lg transition-all duration-200 disabled:opacity-50"
                >
                  {loading ? 'Сохранение...' : '💾 Сохранить'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowEditModal(false)}
                  className="flex-1 py-2.5 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold rounded-xl transition-all duration-200"
                >
                  Отмена
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Admin;