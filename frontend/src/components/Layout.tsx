import React, { useState, useRef, useEffect } from 'react';
import { Link, Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Layout: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const handleLogout = () => {
    logout();
    navigate('/login');
    setIsMenuOpen(false);
    setIsDropdownOpen(false);
  };

  // Закрытие меню при клике вне его
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Закрытие выпадающего списка при клике вне его
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Проверка активной страницы
  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* НАВИГАЦИЯ */}
      <nav className="bg-white/95 backdrop-blur-sm shadow-sm sticky top-0 z-50">
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-center h-16">

            {/* Логотип */}
            <Link to="/" className="text-2xl font-bold bg-gradient-to-r from-blue-700 to-indigo-700 bg-clip-text text-transparent hover:opacity-80 transition">
              🎹 PianoTechniciansClub
            </Link>

            {/* Бургер-меню (для телефонов) */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="flex flex-col gap-1.5 p-2 hover:bg-gray-100 rounded-lg transition md:hidden"
            >
              <span className={`w-6 h-0.5 bg-gray-600 transition-all duration-300 ${isMenuOpen ? 'rotate-45 translate-y-2' : ''}`}></span>
              <span className={`w-6 h-0.5 bg-gray-600 transition-all duration-300 ${isMenuOpen ? 'opacity-0' : ''}`}></span>
              <span className={`w-6 h-0.5 bg-gray-600 transition-all duration-300 ${isMenuOpen ? '-rotate-45 -translate-y-2' : ''}`}></span>
            </button>

            {/* Меню для компьютеров */}
            <div className="hidden md:flex items-center gap-6">

              {/* Главная */}
              <Link to="/" className={`hover:text-indigo-700 transition ${isActive('/') ? 'text-indigo-700 font-semibold' : 'text-gray-600'}`}>
                🏠 Главная
              </Link>

              {/* Ссылки для подписанных участников */}
              {user?.is_subscribed && (
                <>
                  <Link to="/calculator" className={`hover:text-indigo-700 transition ${isActive('/calculator') ? 'text-indigo-700 font-semibold' : 'text-gray-600'}`}>
                    🧮 Калькулятор
                  </Link>
                  <Link to="/age" className={`hover:text-indigo-700 transition ${isActive('/age') ? 'text-indigo-700 font-semibold' : 'text-gray-600'}`}>
                    🔍 Атлас
                  </Link>
                  {/* 👇 НОВАЯ ССЫЛКА - РЕГУЛИРОВКА */}
                  <Link to="/regulating" className={`hover:text-indigo-700 transition ${isActive('/regulating') ? 'text-indigo-700 font-semibold' : 'text-gray-600'}`}>
                    🔧 Регулировка
                  </Link>
                </>
              )}

              {/* Ссылка для админов */}
              {(user?.is_admin || user?.is_super_admin) && (
                <Link to="/admin" className={`hover:text-indigo-700 transition ${isActive('/admin') ? 'text-indigo-700 font-semibold' : 'text-gray-600'}`}>
                  👑 Админ
                </Link>
              )}

              {/* Профиль пользователя (если авторизован) */}
              {user ? (
                <div className="relative" ref={dropdownRef}>
                  <button
                    onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                    className="flex items-center gap-2 px-3 py-2 rounded-xl hover:bg-gray-100 transition"
                  >
                    <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-600 to-indigo-600 flex items-center justify-center text-white font-bold text-sm shadow-md">
                      {user.first_name?.charAt(0).toUpperCase() || 'U'}
                    </div>
                    <span className="text-gray-700 font-medium">{user.username}</span>
                    <svg className={`w-4 h-4 text-gray-500 transition-transform duration-200 ${isDropdownOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>

                  {/* Выпадающее меню профиля */}
                  {isDropdownOpen && (
                    <div className="absolute right-0 mt-2 w-56 bg-white rounded-2xl shadow-xl py-2 z-50 border border-gray-100">
                      <div className="px-4 py-2 border-b border-gray-100">
                        <p className="text-sm font-semibold text-gray-900">{user.first_name} {user.last_name || ''}</p>
                        <p className="text-xs text-gray-500">@{user.username}</p>
                        {user.is_super_admin && <span className="text-xs text-amber-600 font-semibold">👑 Супер-админ</span>}
                        {user.is_admin && !user.is_super_admin && <span className="text-xs text-indigo-600 font-semibold">⭐ Админ</span>}
                      </div>
                      <Link to="/profile" className="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-indigo-50 transition" onClick={() => setIsDropdownOpen(false)}>
                        <span>👤</span> Профиль
                      </Link>
                      <hr className="my-1 border-gray-100" />
                      <button onClick={handleLogout} className="flex items-center gap-3 w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition text-left">
                        <span>🚪</span> Выйти
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                // Кнопка входа
                <Link to="/login" className="px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-xl shadow-md hover:shadow-lg transition-all duration-200">
                  🔑 Вход
                </Link>
              )}
            </div>
          </div>

          {/* МОБИЛЬНОЕ МЕНЮ (для телефонов) */}
          <div
            ref={menuRef}
            className={`md:hidden overflow-hidden transition-all duration-300 ease-in-out ${
              isMenuOpen ? 'max-h-96 opacity-100 pb-4' : 'max-h-0 opacity-0'
            }`}
          >
            <div className="flex flex-col gap-1 bg-white/50 backdrop-blur-sm rounded-xl p-3">

              <Link to="/" className="px-3 py-2 rounded-lg hover:bg-gray-100 transition" onClick={() => setIsMenuOpen(false)}>
                🏠 Главная
              </Link>

              {user?.is_subscribed && (
                <>
                  <Link to="/calculator" className="px-3 py-2 rounded-lg hover:bg-gray-100 transition" onClick={() => setIsMenuOpen(false)}>
                    🧮 Калькулятор
                  </Link>
                  <Link to="/age" className="px-3 py-2 rounded-lg hover:bg-gray-100 transition" onClick={() => setIsMenuOpen(false)}>
                    🔍 Атлас
                  </Link>
                  {/* 👇 НОВАЯ ССЫЛКА В МОБИЛЬНОМ МЕНЮ */}
                  <Link to="/regulating" className="px-3 py-2 rounded-lg hover:bg-gray-100 transition" onClick={() => setIsMenuOpen(false)}>
                    🔧 Регулировка
                  </Link>
                </>
              )}

              {(user?.is_admin || user?.is_super_admin) && (
                <Link to="/admin" className="px-3 py-2 rounded-lg hover:bg-gray-100 transition" onClick={() => setIsMenuOpen(false)}>
                  👑 Админ
                </Link>
              )}

              {user ? (
                <>
                  <Link to="/profile" className="px-3 py-2 rounded-lg hover:bg-gray-100 transition" onClick={() => setIsMenuOpen(false)}>
                    👤 Профиль
                  </Link>
                  <button onClick={handleLogout} className="px-3 py-2 rounded-lg hover:bg-red-50 text-red-600 transition text-left">
                    🚪 Выйти
                  </button>
                </>
              ) : (
                <Link to="/login" className="px-3 py-2 rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-center" onClick={() => setIsMenuOpen(false)}>
                  🔑 Вход
                </Link>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* КОНТЕНТ СТРАНИЦЫ */}
      <div className="container mx-auto p-4 md:p-8">
        <Outlet />
      </div>
    </div>
  );
};

export default Layout;