import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

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

interface WhitelistUser {
  id: number;
  telegram_id: number;
  username: string;
  first_name: string;
  last_name: string | null;
  is_admin: boolean;
  is_super_admin: boolean;
}

interface AccessRequest {
  id: number;
  user_id: number;
  username: string;
  full_name: string;
  email: string;
  message: string | null;
  status: string;
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

interface Stats {
  total_users: number;
  subscribed_users: number;
  admin_users: number;
  pending_requests: number;
  total_calculations: number;
}

const Admin: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState<'stats' | 'users' | 'whitelist' | 'requests' | 'brands'>('stats');
  const [stats, setStats] = useState<Stats | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [whitelist, setWhitelist] = useState<WhitelistUser[]>([]);
  const [requests, setRequests] = useState<AccessRequest[]>([]);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);

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

  useEffect(() => {
    loadStats();
    loadUsers();
    loadWhitelist();
    loadRequests();
    loadBrands();
  }, []);

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
    const token = localStorage.getItem('token');
    if (!token) {
      alert('❌ Токен не найден. Выйдите и зайдите снова.');
      return;
    }

    if (!window.confirm(`Вы уверены, что хотите ${action === 'approve' ? 'одобрить' : 'отклонить'} заявку?`)) return;

    try {
      const response = await fetch(`http://localhost:8000/api/v1/admin/requests/${requestId}/${action}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      if (response.ok) {
        alert(action === 'approve' ? '✅ Заявка одобрена, пользователь создан' : '❌ Заявка отклонена');
        loadRequests();
        loadUsers();
        loadStats();
        loadWhitelist();
      } else {
        alert('❌ Ошибка: ' + (data.detail || 'Неизвестная ошибка'));
      }
    } catch (error) {
      console.error('Ошибка:', error);
      alert('❌ Ошибка сети. Проверьте, запущен ли бэкенд.');
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
      <div className="glass-card p-8">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-3xl font-bold text-white">👑 Админ-панель</h2>
            <p className="text-white/50 mt-1">Управление клубом</p>
          </div>
          <div className="flex gap-3">
            <button onClick={() => navigate(-1)} className="glass-btn">← Назад</button>
            <button onClick={() => { logout(); navigate('/login'); }} className="glass-btn glass-btn-danger">🚪 Выйти</button>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 mb-6 border-b border-white/10 pb-2">
          {['stats', 'users', 'whitelist', 'requests', 'brands'].map((tab) => {
            const labels: Record<string, string> = {
              stats: '📊 Статистика',
              users: '👥 Пользователи',
              whitelist: '🔓 Белый список',
              requests: '📩 Заявки',
              brands: '📖 Атлас'
            };
            return (
              <button
                key={tab}
                onClick={() => setActiveTab(tab as any)}
                className={`px-5 py-2.5 rounded-xl font-medium transition-all ${
                  activeTab === tab
                    ? 'glass-btn glass-btn-primary'
                    : 'text-white/50 hover:text-white hover:bg-white/10'
                }`}
              >
                {labels[tab]}
                {tab === 'requests' && stats?.pending_requests !== undefined && stats.pending_requests > 0 && (
                  <span className="ml-1 px-2 py-0.5 text-xs bg-red-500/30 text-red-300 rounded-full">
                    {stats.pending_requests}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {activeTab === 'stats' && stats && (
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="glass-card p-5 text-center"><div className="text-2xl font-bold text-white">{stats.total_users}</div><div className="text-sm text-white/50 mt-1">Всего пользователей</div></div>
            <div className="glass-card p-5 text-center border border-green-500/20"><div className="text-2xl font-bold text-green-300">{stats.subscribed_users}</div><div className="text-sm text-white/50 mt-1">Подписаны</div></div>
            <div className="glass-card p-5 text-center border border-purple-500/20"><div className="text-2xl font-bold text-purple-300">{stats.admin_users}</div><div className="text-sm text-white/50 mt-1">Админы</div></div>
            <div className="glass-card p-5 text-center border border-orange-500/20"><div className="text-2xl font-bold text-orange-300">{stats.total_calculations || 0}</div><div className="text-sm text-white/50 mt-1">Расчётов</div></div>
            <div className="glass-card p-5 text-center border border-yellow-500/20"><div className="text-2xl font-bold text-yellow-300">{stats.pending_requests}</div><div className="text-sm text-white/50 mt-1">Заявок</div></div>
          </div>
        )}

        {activeTab === 'users' && (
          <div>
            <div className="flex justify-between items-center mb-4 flex-wrap gap-2">
              <h3 className="text-xl font-semibold text-white">👥 Пользователи</h3>
              <input type="text" placeholder="🔍 Поиск..." value={search} onChange={(e) => setSearch(e.target.value)} className="glass-input" />
            </div>
            <div className="glass-table">
              <table className="min-w-full divide-y divide-white/5 text-sm">
                <thead><tr>
                  <th className="px-4 py-3 text-left font-medium text-white/40">ID</th>
                  <th className="px-4 py-3 text-left font-medium text-white/40">Имя</th>
                  <th className="px-4 py-3 text-left font-medium text-white/40">Telegram ID</th>
                  <th className="px-4 py-3 text-left font-medium text-white/40">Статус</th>
                  <th className="px-4 py-3 text-left font-medium text-white/40">Роль</th>
                  <th className="px-4 py-3 text-left font-medium text-white/40">Действия</th>
                </tr></thead>
                <tbody>
                  {filteredUsers.map((u) => (
                    <tr key={u.id} className="hover:bg-white/5 transition">
                      <td className="px-4 py-3 text-white/60">{u.id}</td>
                      <td className="px-4 py-3 font-medium text-white">{u.first_name} {u.last_name}</td>
                      <td className="px-4 py-3 text-white/60">{u.telegram_id}</td>
                      <td className="px-4 py-3">{u.is_subscribed ? <span className="px-2.5 py-1 bg-green-500/20 text-green-300 rounded-full text-xs font-semibold border border-green-500/20">✅ Подписан</span> : <span className="px-2.5 py-1 bg-white/5 text-white/40 rounded-full text-xs font-semibold">⏳ Ожидает</span>}</td>
                      <td className="px-4 py-3 text-white/60">{u.is_super_admin ? '👑 Супер-админ' : u.is_admin ? '⭐ Админ' : '👤 Пользователь'}</td>
                      <td className="px-4 py-3 space-x-2">
                        {!u.is_super_admin && (
                          <>
                            <button onClick={() => handleEditUser(u)} className="text-blue-400 hover:text-blue-300 transition font-medium">✏️ Редактировать</button>
                            <button onClick={() => handleDeleteUser(u.id)} className="text-red-400 hover:text-red-300 transition font-medium">🗑️ Удалить</button>
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

        {activeTab === 'whitelist' && (
          <div>
            <h3 className="text-xl font-semibold text-white mb-4">🔓 Белый список</h3>
            {user?.is_super_admin && (
              <form onSubmit={handleAddAdmin} className="mb-4 flex gap-2 flex-wrap">
                <input type="number" placeholder="Telegram ID" value={newAdminId} onChange={(e) => setNewAdminId(e.target.value)} className="glass-input" required />
                <button type="submit" disabled={loading} className="glass-btn glass-btn-success">➕ Добавить админа</button>
              </form>
            )}
            <div className="glass-table">
              <table className="min-w-full divide-y divide-white/5 text-sm">
                <thead><tr>
                  <th className="px-4 py-3 text-left font-medium text-white/40">ID</th>
                  <th className="px-4 py-3 text-left font-medium text-white/40">Имя</th>
                  <th className="px-4 py-3 text-left font-medium text-white/40">Telegram ID</th>
                  <th className="px-4 py-3 text-left font-medium text-white/40">Роль</th>
                  <th className="px-4 py-3 text-left font-medium text-white/40">Действия</th>
                </tr></thead>
                <tbody>
                  {whitelist.map((u) => (
                    <tr key={u.id} className="hover:bg-white/5 transition">
                      <td className="px-4 py-3 text-white/60">{u.id}</td>
                      <td className="px-4 py-3 font-medium text-white">{u.first_name} {u.last_name}</td>
                      <td className="px-4 py-3 text-white/60">{u.telegram_id}</td>
                      <td className="px-4 py-3 text-white/60">{u.is_super_admin ? '👑 Супер-админ' : '⭐ Админ'}</td>
                      <td className="px-4 py-3">
                        {!u.is_super_admin && user?.is_super_admin && (
                          <button onClick={() => handleRemoveAdmin(u.telegram_id)} className="text-red-400 hover:text-red-300 transition font-medium">🗑️ Удалить</button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'requests' && (
          <div>
            <h3 className="text-xl font-semibold text-white mb-4">📩 Заявки на доступ</h3>
            {requests.length === 0 ? (
              <div className="text-center py-8 text-white/50"><div className="text-4xl mb-2">✅</div><p>Нет активных заявок</p></div>
            ) : (
              <div className="glass-table">
                <table className="min-w-full divide-y divide-white/5 text-sm">
                  <thead><tr>
                    <th className="px-4 py-3 text-left font-medium text-white/40">Пользователь</th>
                    <th className="px-4 py-3 text-left font-medium text-white/40">Email</th>
                    <th className="px-4 py-3 text-left font-medium text-white/40">Сообщение</th>
                    <th className="px-4 py-3 text-left font-medium text-white/40">Дата</th>
                    <th className="px-4 py-3 text-left font-medium text-white/40">Действия</th>
                  </tr></thead>
                  <tbody>
                    {requests.map((r) => (
                      <tr key={r.id} className="hover:bg-white/5 transition">
                        <td className="px-4 py-3 font-medium text-white">{r.full_name}</td>
                        <td className="px-4 py-3 text-white/60">{r.email}</td>
                        <td className="px-4 py-3 text-white/60">{r.message || '—'}</td>
                        <td className="px-4 py-3 text-white/40 text-sm">{new Date(r.created_at).toLocaleDateString()}</td>
                        <td className="px-4 py-3 space-x-2">
                          {r.status === 'pending' ? (
                            <>
                              <button onClick={() => handleProcessRequest(r.id, 'approve')} className="glass-btn glass-btn-success text-sm py-1.5 px-3">✅ Одобрить</button>
                              <button onClick={() => handleProcessRequest(r.id, 'reject')} className="glass-btn glass-btn-danger text-sm py-1.5 px-3">❌ Отклонить</button>
                            </>
                          ) : (
                            <span className="text-white/40">{r.status === 'approved' ? '✅ Одобрена' : '❌ Отклонена'}</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === 'brands' && (
          <div>
            <div className="flex justify-between items-center mb-4 flex-wrap gap-2">
              <h3 className="text-xl font-semibold text-white">📖 Атлас (Бренды)</h3>
              <button onClick={() => setShowAddForm(!showAddForm)} className="glass-btn glass-btn-success">{showAddForm ? '❌ Отмена' : '➕ Добавить бренд'}</button>
            </div>
            {showAddForm && (
              <form onSubmit={handleAddBrand} className="mb-6 glass p-6 rounded-2xl">
                <h4 className="font-semibold text-white mb-4">➕ Добавление бренда</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <input type="text" placeholder="Название бренда *" value={newBrand.name} onChange={(e) => setNewBrand({...newBrand, name: e.target.value})} className="glass-input" required />
                  <input type="text" placeholder="Страна *" value={newBrand.country} onChange={(e) => setNewBrand({...newBrand, country: e.target.value})} className="glass-input" required />
                  <select value={newBrand.type} onChange={(e) => setNewBrand({...newBrand, type: e.target.value})} className="glass-select">
                    <option value="foreign">🌍 Иностранные</option>
                    <option value="russian">🇷🇺 Отечественные</option>
                  </select>
                  <input type="text" placeholder="Дополнительная информация" value={newBrand.info} onChange={(e) => setNewBrand({...newBrand, info: e.target.value})} className="glass-input" />
                </div>
                <h5 className="font-medium mt-4 mb-2 text-white/70">📊 Диапазоны серийных номеров</h5>
                {newBrand.ranges.map((range, index) => (
                  <div key={index} className="flex gap-2 items-center mb-2 flex-wrap">
                    <input type="number" placeholder="Начало" value={range.serial_start} onChange={(e) => updateRange(index, 'serial_start', e.target.value)} className="glass-input w-24" />
                    <span className="text-white/40">—</span>
                    <input type="number" placeholder="Конец" value={range.serial_end} onChange={(e) => updateRange(index, 'serial_end', e.target.value)} className="glass-input w-24" />
                    <input type="number" placeholder="Год" value={range.year} onChange={(e) => updateRange(index, 'year', e.target.value)} className="glass-input w-24" />
                    <button type="button" onClick={() => removeRange(index)} className="text-red-400 hover:text-red-300 px-2 text-xl font-bold">✕</button>
                  </div>
                ))}
                <button type="button" onClick={addRange} className="mt-2 text-blue-400 hover:text-blue-300 text-sm font-medium">+ Добавить диапазон</button>
                <div className="mt-4 flex gap-3">
                  <button type="submit" disabled={loading} className="glass-btn glass-btn-primary">{loading ? 'Добавление...' : '✅ Добавить бренд'}</button>
                </div>
              </form>
            )}
            <div className="glass-table">
              <table className="min-w-full divide-y divide-white/5 text-sm">
                <thead><tr>
                  <th className="px-4 py-3 text-left font-medium text-white/40">Название</th>
                  <th className="px-4 py-3 text-left font-medium text-white/40">Страна</th>
                  <th className="px-4 py-3 text-left font-medium text-white/40">Тип</th>
                  <th className="px-4 py-3 text-left font-medium text-white/40">Диапазонов</th>
                  <th className="px-4 py-3 text-left font-medium text-white/40">Действия</th>
                </tr></thead>
                <tbody>
                  {brands.map((b) => (
                    <tr key={b.id} className="hover:bg-white/5 transition">
                      <td className="px-4 py-3 font-medium text-white">{b.name}</td>
                      <td className="px-4 py-3 text-white/60">{b.country}</td>
                      <td className="px-4 py-3"><span className={`px-2.5 py-1 text-xs rounded-full font-semibold ${b.type === 'foreign' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/20' : 'bg-red-500/20 text-red-300 border border-red-500/20'}`}>{b.type === 'foreign' ? '🌍 Иностранный' : '🇷🇺 Отечественный'}</span></td>
                      <td className="px-4 py-3 text-center text-white/60">{b.ranges_count}</td>
                      <td className="px-4 py-3">
                        <button onClick={() => handleDeleteBrand(b.id)} className="text-red-400 hover:text-red-300 transition font-medium">🗑️ Удалить</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {showEditModal && editingUser && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="glass-card p-8 max-w-md w-full">
            <h3 className="text-2xl font-bold text-white mb-4">✏️ Редактирование пользователя</h3>
            <form onSubmit={handleSaveUser} className="space-y-4">
              <div><label className="block text-sm font-medium text-white/70">Имя</label><input type="text" value={editForm.first_name} onChange={(e) => setEditForm({...editForm, first_name: e.target.value})} className="glass-input w-full" required /></div>
              <div><label className="block text-sm font-medium text-white/70">Фамилия</label><input type="text" value={editForm.last_name} onChange={(e) => setEditForm({...editForm, last_name: e.target.value})} className="glass-input w-full" /></div>
              <div><label className="block text-sm font-medium text-white/70">Имя пользователя</label><input type="text" value={editForm.username} onChange={(e) => setEditForm({...editForm, username: e.target.value})} className="glass-input w-full" required /></div>
              <div><label className="block text-sm font-medium text-white/70">Новый пароль</label><input type="text" placeholder="Оставьте пустым" value={editForm.new_password} onChange={(e) => setEditForm({...editForm, new_password: e.target.value})} className="glass-input w-full" /></div>
              <div className="flex items-center gap-4">
                <label className="flex items-center gap-2 cursor-pointer text-white/70"><input type="checkbox" checked={editForm.is_subscribed} onChange={(e) => setEditForm({...editForm, is_subscribed: e.target.checked})} className="w-4 h-4 accent-indigo-500" /> Подписан</label>
                <label className="flex items-center gap-2 cursor-pointer text-white/70"><input type="checkbox" checked={editForm.is_admin} onChange={(e) => setEditForm({...editForm, is_admin: e.target.checked})} className="w-4 h-4 accent-indigo-500" disabled={editingUser.is_super_admin} /> Администратор</label>
              </div>
              <div className="flex gap-3 mt-4">
                <button type="submit" disabled={loading} className="flex-1 glass-btn glass-btn-primary">{loading ? 'Сохранение...' : '💾 Сохранить'}</button>
                <button type="button" onClick={() => setShowEditModal(false)} className="flex-1 glass-btn">Отмена</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Admin;